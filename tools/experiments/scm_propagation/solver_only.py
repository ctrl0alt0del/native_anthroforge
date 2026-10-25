"""Owned scene adapter for direct native SQP, with no planner or seed resampling."""

import ctypes as c
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

import numpy as np

from anthroforge.application import routing_evaluation, surface_providers
from anthroforge.core.routing_obstacles import references
from anthroforge.native import paths
from anthroforge.native.mesh import INT64, D, doubles, pointer
from anthroforge.native.routing import Report

IP = c.POINTER(c.c_int)
H = c.c_void_p


def library():
    lib = c.CDLL(str(Path("build/scm-ribs-distortion/native/af_scm_solver_only.dll").resolve()))
    lib.scm_solver_scene.argtypes = [c.POINTER(D), IP, c.POINTER(INT64), IP, D, c.c_int, c.c_double]
    lib.scm_solver_scene.restype = H
    lib.scm_solver_run.argtypes = [H, D, c.c_int, c.c_int, c.c_int, c.c_int, c.c_int, D, INT64, D]
    lib.scm_solver_run.restype = c.c_int
    lib.scm_solver_release.argtypes = [H]
    lib.scm_solver_error.restype = c.c_char_p
    return lib


class Scene:
    def __init__(self, lib, providers, radius):
        self.lib, self.providers = lib, providers
        self.handle = self.capture(radius)
        if not self.handle:
            raise ValueError(lib.scm_solver_error().decode())

    def capture(self, radius):
        vertices = [p.resource.mesh.array(0) for p in self.providers]
        faces = [np.asarray(p.resource.mesh.array(3), dtype=np.int64) for p in self.providers]
        count = len(vertices)
        vp = (D * count)(*(pointer(v) for v in vertices))
        fp = (INT64 * count)(*(f.ctypes.data_as(INT64) for f in faces))
        vc, fc = (
            (c.c_int * count)(*(len(v) for v in vertices)),
            (c.c_int * count)(*(len(f) for f in faces)),
        )
        matrices = doubles([p.frame for p in self.providers])
        return self.lib.scm_solver_scene(vp, vc, fp, fc, pointer(matrices), count, radius)

    def __del__(self):
        if getattr(self, "handle", None):
            self.lib.scm_solver_release(self.handle)


class Cache:
    def __init__(self):
        self.lib, self.values, self.timings = library(), {}, []

    def scene(self, context, item):
        refs, providers = surface_inputs(context, item)
        key = (
            tuple((p.resource.mesh.handle, p.frame) for p in providers),
            item.engine_settings.radius,
        )
        if key not in self.values:
            start = perf_counter()
            self.values[key] = Scene(self.lib, providers, item.engine_settings.radius)
            self.timings.append(dict(surfaces=len(refs), ms=(perf_counter() - start) * 1000))
        return self.values[key], routing_evaluation.owners(item, refs)


def surface_inputs(context, item):
    refs = surface_providers.query_references(
        context.engine, context.document, context.assets, references(context.document, item)
    )
    return refs, [
        surface_providers.get(context.engine, context.document, context.assets, ref) for ref in refs
    ]


@dataclass
class Result:
    path: object
    authored: object
    diagnostics: Report
    success: bool
    planner_used: bool = False


def evaluate(context, item, seed, scene, owners, seed_reference=False):
    points = doubles(seed.path.array()[:, :3])
    expected = np.array([p.position for p in item.points])
    np.testing.assert_allclose(points[[0, -1]], expected, atol=1e-8, rtol=0)
    output, diagnostics, valid = solve_points(
        scene, points, owners, item.engine_settings.accepted_steps, seed_reference
    )
    path = result_path(context.engine, seed, output)
    return Result(path, item, diagnostics, bool(valid))


def solve_points(scene, points, owners, cap, seed_reference):
    output = np.empty_like(points)
    counters, measures = np.zeros(8, dtype=np.int64), np.zeros(8)
    valid = invoke(scene, points, owners, cap, seed_reference, output, counters, measures)
    return output, Report(tuple(counters.tolist()), tuple(measures.tolist())), valid


def invoke(scene, points, owners, cap, seed_reference, output, counters, measures):
    inputs = scene.handle, pointer(points), len(points), owners[0], owners[-1], cap, seed_reference
    outputs = pointer(output), counters.ctypes.data_as(INT64), pointer(measures)
    valid = scene.lib.scm_solver_run(*inputs, *outputs)
    if valid < 0:
        raise ValueError(scene.lib.scm_solver_error().decode())
    return valid


def result_path(engine, seed, positions):
    values = np.zeros((len(positions), 11))
    values[:, :3] = positions
    values[:, 5] = values[:, 7] = 1  # Same Z tangent / Y normal inputs as ROUTED result().
    values[:, 9:] = seed.path.array()[:, 9:]
    parameters = np.linspace(0, 1, len(values))
    raw = paths.restore(engine, values, parameters, False)
    return paths.restore(engine, paths.body(raw), parameters, False)
