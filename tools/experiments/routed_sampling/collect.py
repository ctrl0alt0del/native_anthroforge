"""Collect comparable geometry and real attachment evidence without changing production."""

import argparse
import json
from pathlib import Path

import native_probe
import numpy as np
import scene

from anthroforge.application import surface_providers
from anthroforge.application.session import Session
from anthroforge.native import path_collisions, paths

IDENTITY = np.eye(4).ravel()


def sampled_path(session, vertices):
    data = np.zeros((len(vertices), 11))
    data[:, :3], data[:, 5], data[:, 7], data[:, 9] = vertices, 1, 1, 1
    return paths.restore(session.engine, data, np.linspace(0, 1, len(data)), False)


def collisions(session, keys, vertices):
    path = sampled_path(session, vertices)
    handles, matrices = surface_providers.inputs(
        session.engine, session.document, session.assets, keys
    )
    result, tolerance = path_collisions.check(
        session.engine, [path_collisions.row(path, IDENTITY, [1, 2])], handles, matrices
    )
    return dict(first_segments=result[0].tolist(), tolerance=tolerance)


def accepted_path(session, key):
    item = session.document.object(key)
    assert item.result.status == "ready", item.result.error
    return session.resources.paths[item.result.asset].path.array().copy()


def accepted_mesh(session, key):
    item = session.document.object(key)
    assert item.result.status == "ready", item.result.error
    return session.assets[item.result.asset].mesh.array(0).copy()


def bindings(session, objects):
    fibers = [session.document.object(k) for k in objects["fibers"]]
    anchors = [session.document.object(k) for k in objects["anchors"]]
    assert all(o.result.status == "ready" for o in [*fibers, *anchors])
    return tuple((f.points, f.bindings, f.attachment_asset) for f in fibers), tuple(
        a.binding for a in anchors
    )


def frame(session, objects, library, output, name):
    rows = [accepted_path(session, key) for key in objects["fibers"]]
    arrays = {f"path{i}": row[:, :3] for i, row in enumerate(rows)}
    result = dict(name=name, route_samples=[len(row) for row in rows], variants={})
    for label, count in (("exact", 0), ("fixed32", 32), ("fixed8", 8)):
        value = native_probe.geometry(library, rows, count)
        arrays.update({label + "_" + k: value[k] for k in ("vertices", "axis", "marker")})
        result["variants"][label] = evidence(session, objects, value)
    verify_frame(session, objects, arrays)
    np.savez(output / f"{name}.npz", **arrays)
    return result


def verify_frame(session, objects, arrays):
    np.testing.assert_allclose(
        arrays["fixed32_vertices"].reshape(-1, 3),
        accepted_mesh(session, objects["uniform"]),
        atol=1e-12,
    )
    arrays["anchor_positions"] = np.array(
        [session.document.object(k).resolved_position for k in objects["anchors"]]
    )


def evidence(session, objects, value):
    geometry = value["vertices"]
    rows = [collisions(session, objects["supports"], geometry[i]) for i in (0, -1)]
    return dict(
        columns=geometry.shape[1],
        vertices=geometry.shape[0] * geometry.shape[1],
        corner_error_m=value["error"],
        boundary_collisions=rows,
        material_probe=value["marker"].tolist(),
    )


def run(session, library, output):
    objects = scene.create(session)
    initial, records = bindings(session, objects), []
    for name, z in (("before", 3), ("blocked", 0), ("restored", 3)):
        scene.move(session, objects["supports"][-1], [0, 0, z])
        assert bindings(session, objects) == initial
        records.append(frame(session, objects, library, output, name))
        session.command("save", path=str(output / f"{name}.anthroforge"), blocked_policy="wait")
    assert all(o.result.status == "ready" for o in session.document.objects if o.result.asset)
    lifecycle(session, objects, initial, output)
    return report(session, records)


def lifecycle(session, objects, initial, output):
    for operation, count in (("undo", 4), ("redo", 3)):
        session.command(operation)
        session.wait()
        assert bindings(session, objects) == initial
        assert [len(accepted_path(session, k)) for k in objects["fibers"]] == [count, count]
    session.command("open", path=str(output / "restored.anthroforge"))
    session.wait()
    assert bindings(session, objects) == initial
    for key in objects["anchors"]:
        np.testing.assert_allclose(
            session.document.object(key).resolved_position,
            session.document.object(key).position,
            atol=1e-10,
        )


def report(session, records):
    markers = [np.array(frame["variants"]["exact"]["material_probe"]) for frame in records]
    np.testing.assert_allclose(markers[0], markers[-1], atol=1e-12)
    return dict(
        frames=records,
        actual_uniform_base_final_bindings_retained=True,
        undo_redo_roundtrip=True,
        errors=session.scheduler.errors,
        exact_transport="isolated coordinate prototype",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("library", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    collect(args)


def collect(args):
    session = Session()
    try:
        report = run(session, native_probe.load(args.library), args.output.resolve())
        (args.output / "comparison.json").write_text(json.dumps(report, indent=2))
        print(json.dumps(report, indent=2))
    finally:
        session.close()


if __name__ == "__main__":
    main()
