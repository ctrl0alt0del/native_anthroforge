"""Native findings, curve metrics and advisory contacts; outside timed evaluation."""

import ctypes as c
from collections import Counter

import numpy as np
from audit import hits
from fairing_run import CONFIGS, OUT, write
from fairing_trial import library
from fixture import fixture

from anthroforge.application import routing_evaluation, surface_providers
from anthroforge.core.entities import IDENTITY
from anthroforge.core.routing_obstacles import references
from anthroforge.native import inspection, path_collisions, paths
from anthroforge.native.mesh import D, GeometryEngine, doubles, pointer


def scan(engine, name, stage):
    data = np.load(OUT / f"{name}-{stage}.npz")
    q, t = data["points"], data["triangles"]
    mesh = engine.create_mesh(q, t.ravel(), np.arange(len(t) + 1) * 3)
    ids, _, truncated = inspection.findings(mesh, IDENTITY, [], [], 4096, 0)
    counts = Counter(int(row[0]) for row in ids)
    return dict(crossings=counts[2], degenerate=counts[1], truncated=truncated)


def metrics(lib, samples):
    raw, result = doubles(samples[:, :3]), np.empty(4)
    lib.fair_metrics(len(raw), pointer(raw), pointer(result))
    return dict(
        zip(
            ("length", "max_edge", "max_turn_radians", "total_turn_radians"),
            result.tolist(),
            strict=True,
        )
    )


def paths_for(context, data, names):
    assets = []
    for name in names:
        saved = np.load(OUT / f"{name}-{data.item.id}.npz")
        assets.append(paths.restore(context.engine, saved["samples"], saved["parameters"], False))
    return assets


def contacts(context, data, assets):
    refs = references(context.document, data.item)
    handles, frames = surface_providers.inputs(
        context.engine, context.document, context.assets, refs
    )
    owners = routing_evaluation.owners(data.item, refs)
    rows = [path_collisions.row(path, data.item.matrix, owners) for path in assets]
    found, tolerance = path_collisions.check(context.engine, rows, handles, frames)
    return [dict(tolerance=float(tolerance), hits=hits(context, refs, row)) for row in found]


def inspect_paths(f, names, output):
    lib = library()
    lib.fair_metrics.argtypes = [c.c_int, D, D]
    for data in f.curves:
        assets = paths_for(f.after, data, names)
        checks = contacts(f.after, data, assets)
        for name, path, check in zip(names, assets, checks, strict=True):
            values = metrics(lib, path.array())
            values["contact_check"] = check
            values["endpoint_error"] = float(
                np.max(np.abs(path.array()[data.pins, :3] - data.goals))
            )
            output[name]["paths"][data.item.id] = values


def run():
    engine = GeometryEngine()
    f = fixture(engine)
    names = ("current", *CONFIGS)
    output = {
        name: dict(paths={}, stages={s: scan(engine, name, s) for s in ("base", "rest", "final")})
        for name in names
    }
    inspect_paths(f, names, output)
    write("quality", output)
    print({name: row["stages"] for name, row in output.items()}, flush=True)


if __name__ == "__main__":
    run()
