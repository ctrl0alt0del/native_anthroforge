"""Compare rebuilt native coarse fields with the unmodified addon source, without Blender."""

import importlib
import json
import sys
import types
from dataclasses import asdict
from pathlib import Path
from time import perf_counter

import numpy as np

from anthroforge.core.skin import EnvelopeSettings
from anthroforge.native.mesh import GeometryEngine
from anthroforge.native.skin_fields import prepare


def source_modules(root):
    package = types.ModuleType("skin_source_control")
    package.__path__ = [str(root / "core" / "draft_skin")]
    sys.modules[package.__name__] = package
    return {
        name: importlib.import_module(f"{package.__name__}.{name}")
        for name in ("grid", "raster", "fields", "settings", "model")
    }


def fixture(seed):
    random = np.random.default_rng(seed)
    vertices = random.uniform(-1, 1, (18, 3))
    faces = np.arange(18).reshape(-1, 3)
    skeletal = np.array([1, 1, 1, 1, 0, 0], dtype=np.uint8)
    collagen = random.uniform(0, 1, 18)
    return vertices, faces, skeletal, collagen


def baseline(modules, inputs, settings, resolution):
    xyz, faces, skeletal, weights = inputs
    config = modules["model"].SkinSolverSettings(**asdict(settings))
    origin, shape, voxel = modules["grid"].grid_spec(xyz, resolution, config)
    raster = modules["raster"].rasterize
    all_surface, _ = raster(xyz, faces, origin, shape, voxel)
    scp_surface, seeds = raster(xyz, faces[skeletal.astype(bool)], origin, shape, voxel, weights)
    distances = modules["settings"].resolved_solver_distances(config, np.ptp(xyz, axis=0).max())
    return fields(modules["fields"], all_surface, scp_surface, seeds, voxel, distances)


def exterior(module, surface, voxel, distances, kind):
    distance = module.surface_distance(surface, voxel)
    return module.exterior_field(
        distance, voxel, distances[f"{kind}_probe"], distances[f"{kind}_offset"]
    )


def fields(module, all_surface, scp_surface, seeds, voxel, distances):
    required = exterior(module, all_surface, voxel, distances, "required")
    rest = exterior(module, scp_surface, voxel, distances, "rest")
    full = module.smooth_max(rest, required, distances["blend_radius"])
    collagen = module.collagen_field(
        scp_surface, seeds, voxel, distances["collagen_inner"], distances["collagen_outer"]
    )
    return required, full, collagen, required + collagen * (full - required)


def compare(engine, modules, seed, resolution):
    inputs, settings = fixture(seed), EnvelopeSettings()
    started = perf_counter()
    expected = baseline(modules, inputs, settings, resolution)
    source_seconds = perf_counter() - started
    started = perf_counter()
    actual = prepare(engine, *inputs, settings=settings, resolution=resolution)
    native_seconds = perf_counter() - started
    errors = [float(np.max(np.abs(actual.array(i) - value))) for i, value in enumerate(expected)]
    actual.close()
    timing = dict(source_seconds=source_seconds, native_seconds=native_seconds)
    return dict(seed=seed, resolution=resolution, maximum_errors=errors, **timing)


def main():
    modules, engine = source_modules(Path(sys.argv[1])), GeometryEngine()
    results = [
        compare(engine, modules, seed, resolution)
        for resolution in (16, 32, 48)
        for seed in range(4)
    ]
    output = Path("build/skin-040/field-parity.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))
    return int(any(max(case["maximum_errors"]) > 1e-12 for case in results))


if __name__ == "__main__":
    raise SystemExit(main())
