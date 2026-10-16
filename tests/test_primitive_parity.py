import json
from pathlib import Path

import numpy as np
import pytest

from anthroforge.application.construction_codec import tuples
from anthroforge.core.construction import Control, Deformer, Target, Thickness
from anthroforge.native import construction as native
from anthroforge.native.mesh import GeometryEngine

REFERENCE = json.loads(
    (Path(__file__).parent / "fixtures/primitives/blender501_deformers.json").read_text()
)
EDGES = json.loads(
    (Path(__file__).parent / "fixtures/primitives/blender501_edges.json").read_text()
)
SHELLS = json.loads(
    (Path(__file__).parent / "fixtures/primitives/blender501_shells.json").read_text()
)


@pytest.fixture(scope="module")
def engine():
    return GeometryEngine()


def result(engine, case):
    points = REFERENCE["vertices"]
    if case["kind"] == "HOOK":
        binding = Deformer("HOOK", "reference", Target("owner"), **tuples(case["options"]))
        return native.hook(engine, points, binding, case["owner"], case["target"], 0)
    if case["kind"] == "LATTICE":
        return lattice_result(engine, points, case)
    offsets = np.cumsum([0, *[len(face) for face in REFERENCE["faces"]]])
    mesh = engine.create_mesh(points, np.concatenate(REFERENCE["faces"]), offsets)
    shell = native.solidify(mesh, Thickness(**tuples(case["options"])), 0)
    return shell.array(0).copy()


def lattice_result(engine, points, case):
    cage = reference_cage(case)
    settings = dict(
        weights=tuple(case["weights"]), invert=case["invert"], strength=case["strength"]
    )
    binding = Deformer("LATTICE", cage.id, Target("owner"), **settings)
    return native.lattice(engine, points, cage, binding, case["owner"], case["target"], 0)


def reference_cage(case):
    cage = Control(
        "Reference",
        "LATTICE",
        points=tuple(map(tuple, case["points"])),
        resolution=tuple(case["resolution"]),
        interpolation=(case["interpolation"],) * 3,
        outside=case["outside"],
        weights=tuple(case.get("cage_weights", ())),
    )
    return cage


@pytest.mark.parametrize(
    "case", REFERENCE["cases"] + EDGES["cases"] + SHELLS["cases"], ids=lambda case: case["kind"]
)
def test_native_modifier_matches_blender_501(engine, case):
    actual, expected = result(engine, case), np.asarray(case["expected"])
    assert len(actual) == len(expected)
    # Solidify's generated vertex order is not an attachment compatibility contract.
    distances = np.linalg.norm(actual[:, None, :] - expected[None, :, :], axis=2)
    assert np.max(np.min(distances, axis=0)) < 2e-5
    assert np.max(np.min(distances, axis=1)) < 2e-5


@pytest.mark.parametrize("case", EDGES["resizes"])
def test_lattice_resize_matches_blender_and_clears_weights(session, case):
    cage = resize_cage(case)
    session.replace_document(controls=(cage,))
    dimensions = list(cage.resolution)
    dimensions["uvw".index(case["axis"])] = case["count"]
    session.command("lattice.resize", control=cage.id, resolution=dimensions)
    session.command("wait", timeout=5)
    result = session.document.control(cage.id)
    assert result.resolution == tuple(case["output_resolution"])
    assert not result.weights and result.interpolation == cage.interpolation
    np.testing.assert_allclose(result.points, case["expected"], atol=2e-5)


def resize_cage(case):
    return Control(
        "Resize reference",
        "LATTICE",
        points=tuple(map(tuple, case["points"])),
        resolution=tuple(case["resolution"]),
        outside=case["outside"],
        weights=tuple(case["weights"]),
    )


@pytest.mark.parametrize("case", SHELLS["cases"])
def test_shell_face_orientation_matches_blender(engine, case):
    faces = REFERENCE["faces"]
    mesh = engine.create_mesh(
        REFERENCE["vertices"], np.concatenate(faces), np.cumsum([0, *map(len, faces)])
    )
    shell = native.solidify(mesh, Thickness(**tuples(case["options"])), 0)
    actual = shell.array(0)
    expected = np.asarray(case["expected"])
    np.testing.assert_allclose(actual, expected, atol=2e-5)
    corners, offsets = shell.array(1), shell.array(2)
    native_faces = [corners[offsets[i] : offsets[i + 1]] for i in range(len(offsets) - 1)]
    native_orientations = {canonical_cycle(face) for face in native_faces}
    assert native_orientations == {canonical_cycle(face) for face in case["faces"]}


def canonical_cycle(face):
    face = list(face)
    start = face.index(min(face))
    return tuple(face[start:] + face[:start])
