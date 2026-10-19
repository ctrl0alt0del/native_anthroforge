"""Serial native routing against evaluated source skull geometry, with report artifacts."""

import json
from dataclasses import replace
from pathlib import Path
from time import perf_counter

import numpy as np

from anthroforge.application.session import Session
from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.curve_engines import RoutingSettings
from anthroforge.core.entities import IDENTITY
from anthroforge.native import point_attachments, routing

OUTPUT = Path("build/020-skull-routing")


def colliders(session, captured):
    return [
        session.engine.create_mesh(
            item["vertices"],
            np.asarray(item["triangles"]).reshape(-1),
            np.arange(len(item["triangles"]) + 1) * 3,
        )
        for item in captured["colliders"]
    ]


def spec(session, meshes, fiber):
    points = [fiber["saved_path"][i] for i in (0, -1)]
    handles, matrices = tuple(mesh.handle for mesh in meshes), (IDENTITY,) * len(meshes)
    owners, _ = point_attachments.capture(session.engine, handles, matrices, points)
    curve = Curve(
        tuple(CurvePoint(position=tuple(point)) for point in points),
        engine_settings=RoutingSettings(samples=64, radius=0.002),
    )
    return routing.Inputs(curve, handles, matrices, owners=tuple(int(i) + 1 for i in owners))


def trial(session, value, label):
    started = perf_counter()
    try:
        path, report = routing.evaluate(session.engine, value)
        return path, dict(name=label, counters=report.counters, points=path.array()[:, :3].tolist())
    except RuntimeError as error:
        return None, dict(name=label, error=str(error))
    finally:
        print(label, round(1000 * (perf_counter() - started), 3), "ms", flush=True)


def trials(session, meshes, captured):
    results = []
    for fiber in captured["fibers"]:
        value = spec(session, meshes, fiber)
        path, result = trial(session, value, fiber["name"] + "-cold")
        results.append(dict(result, owners=value.owners))
        if path:
            _, continued = trial(session, replace(value, warm=path), fiber["name"] + "-warm")
            results.append(continued)
    return results


def run():
    captured = json.loads(Path("build/skull-routing-inputs.json").read_text())
    OUTPUT.mkdir(parents=True, exist_ok=True)
    session = Session()
    try:
        meshes = colliders(session, captured)
        session.command("profile.start")
        results = trials(session, meshes, captured)
        session.command("profile.stop", path=str(OUTPUT / "routing.afprofile.zip"), wait=True)
        (OUTPUT / "results.json").write_text(json.dumps(results, indent=2))
        print(json.dumps([{k: v for k, v in row.items() if k != "points"} for row in results]))
    finally:
        session.close()


if __name__ == "__main__":
    run()
