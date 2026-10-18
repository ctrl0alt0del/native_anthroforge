"""Run the donor solver on pinned evaluated skull inputs; never modify the blend file."""

import importlib
import json
import sys
from dataclasses import replace
from pathlib import Path

from capture_routing_reference import request, source_hashes


def snapshots(captured):
    contracts = importlib.import_module("core.vcp.v2.contracts")
    return tuple(
        contracts.V2ColliderSnapshot(c["name"], c["name"], c["vertices"], c["triangles"])
        for c in captured["colliders"]
    )


def continued(value, result):
    module = importlib.import_module("core.vcp.v3.warm")
    state = module._warm_state(result.points, (0, 63), value.anchors, "fixture", "fixture")
    seed = module._remap(state, 64, value.anchors)
    return replace(value, warm_seed=tuple(map(tuple, seed)))


def solve(captured, fiber, owners):
    solver = importlib.import_module("core.vcp.v3.production").solve_v3
    points = [fiber["saved_path"][i] for i in (0, -1)]
    names = tuple(captured["colliders"][i - 1]["name"] for i in owners)
    value = request(points, colliders=snapshots(captured), owners=names, samples=64)
    result = solver(value).result
    warm = solver(continued(value, result)).result
    print(fiber["name"], result.validated, warm.validated, flush=True)
    return record(fiber["name"], points, owners, result, warm)


def record(name, points, owners, result, warm):
    return dict(
        name=name,
        points=points,
        owners=owners,
        closed=False,
        samples=64,
        radius=0.002,
        accepted_steps=24,
        result=result.points,
        warm=warm.points,
        validated=result.validated,
        warm_validated=warm.validated,
    )


def run(addon, output):
    sys.path.insert(0, str(addon))
    captured = json.loads(Path("build/skull-routing-inputs.json").read_text())
    probes = json.loads(Path("build/020-skull-routing/results.json").read_text())
    owners = {row["name"].removesuffix("-cold"): row["owners"] for row in probes if "owners" in row}
    cases = [solve(captured, fiber, owners[fiber["name"]]) for fiber in captured["fibers"]]
    source = {key: captured[key] for key in ("source", "sha256", "blender", "build")}
    value = dict(
        source=source, addon=source_hashes(addon), colliders=captured["colliders"], cases=cases
    )
    output.write_text(json.dumps(value, separators=(",", ":"), allow_nan=False) + "\n")


if __name__ == "__main__":
    run(Path(sys.argv[1]).resolve(), Path(sys.argv[2]))
