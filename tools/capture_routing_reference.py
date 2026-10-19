"""Capture compact production-addon routing cases without Blender or desktop interaction."""

import hashlib
import importlib
import json
import sys
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import numpy as np


def anchors(points, owners, closed):
    c = importlib.import_module("core.vcp.v2.contracts")
    anchors = tuple(
        c.V2Anchor(p, owners[i] if owners else "", c.V2AnchorRole.TOUCH, i)
        for i, p in enumerate(points)
    )
    if not closed:
        anchors = (
            replace(anchors[0], role=c.V2AnchorRole.ENDPOINT_A),
            *anchors[1:-1],
            replace(anchors[-1], role=c.V2AnchorRole.ENDPOINT_B),
        )
    return anchors


def request(points, closed=False, colliders=(), owners=(), samples=32):
    c = importlib.import_module("core.vcp.v2.contracts")
    scales = importlib.import_module("core.vcp.v2.scales")
    settings = c.V2Settings(
        topology=c.V2Topology.CYCLIC if closed else c.V2Topology.OPEN,
        node_count=samples,
        max_accepted_steps=24,
    )
    bounds = [SimpleNamespace(vertices=np.asarray(row.vertices)) for row in colliders]
    tolerances = scales.resolve_tolerances(bounds, 0.002, settings.quality)
    identity = (1, "fixture", "fixture-root", "fixture")
    policy = c.V2CollisionPolicy(collision_radius=0.002)
    return c.V2Request(
        *identity, settings, tolerances, policy, anchors(points, owners, closed), colliders
    )


def case(name, points, closed=False, colliders=(), owners=(), samples=32):
    production = importlib.import_module("core.vcp.v3.production")
    value = request(points, closed, colliders, owners, samples)
    result = production.solve_v3(value).result
    payload = case_inputs(name, points, closed, colliders, owners, samples)
    return dict(
        payload,
        result=result.points,
        validated=result.validated,
        termination=result.termination.value,
    )


def case_inputs(name, points, closed, colliders, owners, samples):
    return dict(
        name=name,
        points=points,
        closed=closed,
        owners=owners,
        samples=samples,
        radius=0.002,
        accepted_steps=24,
        colliders=[dict(vertices=c.vertices, triangles=c.triangles) for c in colliders],
    )


BOX_TRIANGLES = [
    (0, 3, 1),
    (0, 2, 3),
    (4, 5, 7),
    (4, 7, 6),
    (0, 1, 5),
    (0, 5, 4),
    (2, 6, 7),
    (2, 7, 3),
    (0, 4, 6),
    (0, 6, 2),
    (1, 3, 7),
    (1, 7, 5),
]


def cube():
    c = importlib.import_module("core.vcp.v2.contracts")
    vertices = [(x, y, z) for x in (-0.3, 0.3) for y in (-0.3, 0.3) for z in (-0.3, 0.3)]
    return c.V2ColliderSnapshot("cube", "cube", vertices, BOX_TRIANGLES)


def source_hashes(addon):
    files = {
        Path(module.__file__).resolve()
        for module in tuple(sys.modules.values())
        if getattr(module, "__file__", None)
    }
    return {
        str(p.relative_to(addon)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(files)
        if p.is_relative_to(addon) and p.suffix == ".py"
    }


def fixtures():
    return [
        case("open-bent", [(0, 0, 0), (1, 1, 0), (3, 0, 0)]),
        case("closed-four", [(1, 0, 0), (0, 1, 0), (-1, 0, 0), (0, -1, 0)], True),
        case("box-detour", [(-1, 0, 0), (1, 0, 0)], colliders=(cube(),)),
        case(
            "bound-box", [(-0.3, 0, 0), (0.3, 0, 0)], colliders=(cube(),), owners=("cube", "cube")
        ),
    ]


def run(addon, output):
    sys.path.insert(0, str(addon))
    rows = fixtures()
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(sources=source_hashes(addon), cases=rows)
    output.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps([dict(name=r["name"], validated=r["validated"]) for r in rows]))


if __name__ == "__main__":
    run(Path(sys.argv[1]).resolve(), Path(sys.argv[2]))
