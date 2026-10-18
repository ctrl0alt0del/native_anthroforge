"""Pinned source-scene constructions, independent of a Blender installation at test time."""

import json
from pathlib import Path

import numpy as np
import pytest

from anthroforge.application.construction_codec import curve as decode_curve
from anthroforge.application.construction_codec import tuples
from anthroforge.core.construction import BodyPiece, Control, Deformer, ResolvedPrimitive, Target
from anthroforge.native import bodies
from anthroforge.native import construction as native
from anthroforge.native.mesh import GeometryEngine

ROOT = Path(__file__).parent / "fixtures/primitives"
SOURCES = [
    json.loads((ROOT / name).read_text())
    for name in ("skeleton_primitives.json", "skull_primitives.json")
]
CURVES = [curve for source in SOURCES for curve in source["curves"]]
CAGES = [cage for source in SOURCES for cage in source["cages"]]


@pytest.fixture(scope="module")
def engine():
    return GeometryEngine()


def curve(case):
    record = dict(case["curve"])
    assert record.pop("radius_interpolation") == record.pop("tilt_interpolation") == "LINEAR"
    return decode_curve(record)


def hooks(engine, points, owner, bindings):
    for item in bindings:
        binding = Deformer("HOOK", "reference", Target("owner"), **tuples(item["options"]))
        points = native.hook(engine, points, binding, owner, item["target"], 0)
    return points


def curve_records(engine, case, definition):
    records = native.resolved_curve(engine, definition)
    points = records[:, [3, 4, 5, 0, 1, 2, 6, 7, 8]].reshape((-1, 3))
    deformed = hooks(engine, points, case["owner"], case["hooks"]).reshape((-1, 9))
    records[:, :9] = deformed[:, [3, 4, 5, 0, 1, 2, 6, 7, 8]]
    return native.resolved_curve(engine, definition, records)


@pytest.mark.parametrize("case", CURVES, ids=lambda c: c["name"] + str(c["shift"]))
def test_reference_anatomical_curve_sampling(engine, case):
    definition = curve(case)
    primitive = ResolvedPrimitive(
        "BODY", curves=(definition,), pieces=(BodyPiece(definition.id),), samples=64
    )
    records = curve_records(engine, case, definition)
    actual = native.sample_curve(engine, definition, primitive, records=records)[:, :3]
    np.testing.assert_allclose(actual, case["samples"], atol=5e-5)


@pytest.mark.parametrize("case", CURVES, ids=lambda c: c["name"] + str(c["shift"]))
def test_reference_anatomical_body_deformation(engine, case):
    definition, body = curve(case), case["body"]
    records = curve_records(engine, case, definition)
    samples = bodies.path(engine, definition, 0, records)
    base = engine.create_mesh(
        body["vertices"], np.concatenate(body["faces"]), np.cumsum([0, *map(len, body["faces"])])
    )
    result = bodies.bend(base, samples, BodyPiece(definition.id), definition.closed, 0)
    np.testing.assert_allclose(result.array(0), body["expected"], atol=5e-5)


@pytest.mark.parametrize("case", CAGES, ids=lambda c: c["name"])
def test_reference_brow_cage_and_hook(engine, case):
    points = hooks(engine, case["points"], case["matrix"], case["hooks"])
    cage = Control(
        "Reference brow",
        "LATTICE",
        points=tuple(map(tuple, points)),
        resolution=tuple(case["resolution"]),
        interpolation=tuple(case["interpolation"]),
        outside=case["outside"],
    )
    binding = Deformer("LATTICE", cage.id, Target("owner"))
    actual = native.lattice(
        engine, case["vertices"], cage, binding, case["matrix"], case["matrix"], 0
    )
    np.testing.assert_allclose(actual, case["expected"], atol=5e-5)
