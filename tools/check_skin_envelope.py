"""Source-controlled complete envelope reconstruction, without touching Blender projects."""

import json
import sys
from dataclasses import asdict, replace
from pathlib import Path
from time import perf_counter

import numpy as np

from anthroforge.core.skin import EnvelopeSettings
from anthroforge.native.mesh import GeometryEngine
from anthroforge.native.skin_fields import prepare
from anthroforge.native.skin_gaps import create


def capture():
    from core.draft_skin.model import SkinCapture, SkinSource
    from tests.unit.test_draft_skin import cube_mesh

    vertices, faces = cube_mesh()
    source = SkinSource(0, "SCP", "cube", "ORIGINAL", "Cube", vertices, faces)
    return SkinCapture(
        "root", (source,), vertices.min(0), vertices.max(0), "fixture", 1 / 24, resolution=24
    )


def baseline(value):
    from core.draft_skin.solver import solve_capture

    started = perf_counter()
    result = solve_capture(value)
    return result, perf_counter() - started


def paired_capture(offset):
    value = capture()
    first = value.sources[0]
    second = replace(
        first,
        source_index=1,
        entity_id="second",
        vertices=first.vertices + np.array([offset, 0, 0]),
    )
    xyz = np.concatenate([first.vertices, second.vertices])
    return replace(value, sources=(first, second), lower=xyz.min(0), upper=xyz.max(0))


def prepare_fields(engine, value, inputs):
    from core.draft_skin.solver import combine_capture

    xyz, faces, _scp, collagen = combine_capture(value)
    settings = EnvelopeSettings(**asdict(value.settings))
    flags = inputs[3][inputs[2], 2]
    return prepare(engine, xyz, faces, flags, collagen, settings, value.resolution)


def standalone(value):
    from core.draft_skin.gap_native import _arrays

    engine = GeometryEngine()
    inputs = _arrays(value)
    started = perf_counter()
    fields = prepare_fields(engine, value, inputs)
    scene = create(engine, *inputs)
    mesh = scene.envelope(fields)
    result = mesh.array(0).copy(), mesh.array(1).reshape(-1, 3).copy()
    return result, perf_counter() - started


def compare(expected, actual):
    vertices, faces = actual
    same_vertices = vertices.shape == expected.vertices.shape
    return dict(
        vertices=len(vertices),
        faces=len(faces),
        source_vertices=len(expected.vertices),
        source_faces=len(expected.triangles),
        maximum_error=float(np.max(np.abs(vertices - expected.vertices)))
        if same_vertices
        else None,
        connectivity_equal=np.array_equal(faces, expected.triangles),
    )


def save(folder, result, expected, actual):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "envelope-parity.json").write_text(json.dumps(result, indent=2))
    np.savez(
        folder / "envelope-parity.npz",
        source=expected.vertices,
        source_faces=expected.triangles,
        native=actual[0],
        native_faces=actual[1],
    )
    print(json.dumps(result, indent=2))


def selected_capture():
    from core.draft_skin.protocol import read_capture

    if len(sys.argv) < 3:
        return capture()
    if sys.argv[2] in ("gap", "contact"):
        return paired_capture(1.2 if sys.argv[2] == "gap" else 0.8)
    value = read_capture(Path(sys.argv[2]))
    names = sys.argv[3].split(",") if len(sys.argv) > 3 else ()
    sources = tuple(s for s in value.sources if not names or s.object_name in names)
    xyz = np.concatenate([s.vertices for s in sources])
    return replace(value, sources=sources, lower=xyz.min(0), upper=xyz.max(0), resolution=48)


def main():
    sys.path.insert(0, str(Path(sys.argv[1])))
    value = selected_capture()
    expected, source_seconds = baseline(value)
    actual, native_seconds = standalone(value)
    result = compare(expected, actual)
    result.update(source_seconds=source_seconds, native_seconds=native_seconds)
    folder = Path(sys.argv[4]) if len(sys.argv) > 4 else Path("build/skin-040/cube")
    save(folder, result, expected, actual)
    return int(result["maximum_error"] != 0 or not result["connectivity_equal"])


if __name__ == "__main__":
    raise SystemExit(main())
