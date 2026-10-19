"""Capture actual addon surface kernels without importing Blender or its addon entrypoint."""

import hashlib
import importlib
import json
import sys
from pathlib import Path
from types import ModuleType

OPEN = [[[0, 0, 0], [0.25, 0.1, 0.2], [1, 0, 0]], [[0, 0.4, 0], [0.6, 0.5, 0.2], [1, 0.4, 0]]]
EXACT = [OPEN[0], [[0, 0.4, 0], [0.1, 0.4, 0], [0.8, 0.6, 0.1], [1, 0.4, 0]]]
CLOSED = [
    [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]],
    [[1, 1, 0.3], [1, 0, 0.3], [0, 0, 0.3], [0, 1, 0.3]],
]
PATCH = [[[0, 0, 0], [2, 0, 0.1], [2, 1, 0], [1, 0.4, 0.05], [0, 1, 0]]]
IRREGULAR = [
    [[0, 0, 0], [1.3, 0, 0], [1, 0.8, 0.1], [-0.2, 1, 0], [-0.4, 0.3, 0]],
    [[0.9, 0.7, 0.4], [1.4, 0.1, 0.3], [0, 0, 0.3], [-0.5, 0.4, 0.4], [-0.2, 1, 0.3]],
]


def package(root):
    module = ModuleType("af_surface_reference")
    module.__path__ = [str(root / "core/vcp")]
    sys.modules[module.__name__] = module
    surface = importlib.import_module(module.__name__ + ".fiber_surface")
    free = importlib.import_module(module.__name__ + ".free_surface")
    return surface, free


def mesh(surface, free, rows, exact, closed, patch):
    if patch:
        spec = surface.FiberSurfaceSpec(
            construction_mode="LOOP_PATCH", exact_samples=True, patch_resolution=3
        )
        value = surface.evaluate_fiber_surface(rows, spec)
        return value.vertices, value.faces
    prepared = (
        free._prepare_rows(rows, closed, True, 1)
        if exact
        else surface.prepare_loft_rows(rows, 5, closed)
    )
    vertices = surface.flatten_surface_rows(prepared)
    faces = surface.build_loft_topology(len(prepared), len(prepared[0]), closed_along=closed)
    return vertices, faces


def result(surface, free, name, rows, exact, closed=False, patch=False):
    vertices, faces = mesh(surface, free, rows, exact, closed, patch)
    return dict(
        name=name,
        rows=rows,
        exact=exact,
        closed=closed,
        patch=patch,
        samples=5,
        patch_resolution=3,
        vertices=vertices,
        faces=faces,
    )


def fixtures(root):
    surface, free = package(root)
    cases = [
        result(surface, free, "uniform_open", OPEN, False),
        result(surface, free, "exact_open", EXACT, True),
        result(surface, free, "closed_alignment", CLOSED, True, True),
        result(surface, free, "irregular_closed_uniform", IRREGULAR, False, True),
        result(surface, free, "irregular_closed_exact", IRREGULAR, True, True),
        result(surface, free, "nonplanar_concave_patch", PATCH, True, True, True),
    ]
    return cases


def capture(root, output):
    files = ["fiber_surface.py", "free_surface.py", "free_path.py"]
    hashes = {
        name: hashlib.sha256((root / "core/vcp" / name).read_bytes()).hexdigest() for name in files
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(dict(source=str(root), sha256=hashes, cases=fixtures(root)), indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    capture(Path(sys.argv[1]), Path("tests/fixtures/surfaces/addon.json"))
