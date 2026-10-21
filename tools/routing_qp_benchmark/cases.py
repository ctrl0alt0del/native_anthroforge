"""Existing, provenance-backed routing fixtures and explicit resolution variants."""

import json
from pathlib import Path

import numpy as np

from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.curve_engines import RoutingSettings, decode
from anthroforge.core.entities import IDENTITY
from anthroforge.native import point_attachments
from anthroforge.native.routing import Inputs

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests/fixtures/routing"
VARIANTS = (
    ("snapped_cube.json", (32, 64, 128, 256), (1, 1)),
    ("solver_fail1.json", (24, 64, 128), (1, 1, 2, 2)),
)


def load(name):
    return json.loads((FIXTURES / name).read_text())


def addon_cases():
    for row in load("addon.json")["cases"]:
        yield dict(row, name="addon-" + row["name"], surfaces=row["colliders"])


def user_cases():
    for fixture, counts, contacts in VARIANTS:
        data = load(fixture)
        for count in counts:
            for bound in (False, True):
                name = f"{Path(fixture).stem}-{count}-{'fiber' if bound else 'curve'}"
                yield dict(
                    data,
                    name=name,
                    samples=count,
                    owners=contacts if bound else (),
                    contacts=contacts,
                )


def skull_cases():
    captured = json.loads((ROOT / "build/skull-routing-inputs.json").read_text())
    for fiber in captured["fibers"]:
        points = [fiber["saved_path"][i] for i in (0, -1)]
        yield dict(
            name="skull-" + fiber["name"],
            points=points,
            samples=64,
            radius=0.002,
            owners=(),
            nearest=True,
            surfaces=captured["colliders"],
        )


def all_cases(skull=False):
    return [*addon_cases(), *user_cases(), *(skull_cases() if skull else ())]


def create_mesh(engine, surface):
    triangles = np.asarray(surface["triangles"], dtype=np.int64).reshape(-1, 3)
    return engine.create_mesh(
        surface["vertices"], triangles.ravel(), np.arange(len(triangles) + 1) * 3
    )


def inputs(engine, case):
    meshes = [create_mesh(engine, surface) for surface in case["surfaces"]]
    settings = dict(case.get("settings", {}), samples=case["samples"])
    settings = (
        decode("ROUTED", settings)
        if "settings" in case
        else RoutingSettings(samples=case["samples"], radius=case.get("radius", 0.002))
    )
    points = tuple(CurvePoint(position=tuple(point)) for point in case["points"])
    curve = Curve(points, closed=case.get("closed", False), engine_settings=settings)
    frames = tuple(tuple(s.get("matrix", IDENTITY)) for s in case["surfaces"])
    handles = tuple(m.handle for m in meshes)
    owners = capture_owners(engine, case, handles, frames)
    return meshes, Inputs(curve, handles, frames, tuple(case.get("matrix", IDENTITY)), owners)


def capture_owners(engine, case, handles, frames):
    if case.get("nearest"):
        owners, _ = point_attachments.capture(engine, handles, frames, case["points"])
        return tuple(int(value) + 1 for value in owners)
    return tuple(int(bool(v)) if isinstance(v, str) else v for v in case["owners"])
