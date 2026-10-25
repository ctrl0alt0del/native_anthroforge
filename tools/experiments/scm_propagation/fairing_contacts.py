"""All-segment diagnostic; no endpoint exemptions and no required clearance radius."""

import ctypes as c

import numpy as np
from fairing_run import OUT, write
from fixture import fixture
from solver_only import Scene, library, surface_inputs

from anthroforge.native.mesh import D, GeometryEngine, doubles, pointer

NAMES = ("current", "c2", "wider", "fair10", "fair20")


def check(scene, points, refs):
    values = doubles(points)
    result = np.empty((len(values) - 1, len(refs)), dtype=np.int32)
    status = scene.lib.scm_surface_contacts(
        scene.handle, pointer(values), len(values), result.ctypes.data_as(c.POINTER(c.c_int))
    )
    if status:
        raise RuntimeError(scene.lib.scm_solver_error().decode())
    return {
        ref.target: np.flatnonzero(result[:, index]).tolist()
        for index, ref in enumerate(refs)
        if result[:, index].any()
    }


def captured(context, curves, lib, baseline=False):
    refs, providers = surface_inputs(context, curves[0].item)
    scene = Scene(lib, providers, 0)
    output = {}
    for data in curves:
        names = ("before",) if baseline else NAMES
        output[data.item.id] = {name: check(scene, points(data, name), refs) for name in names}
    return output


def points(data, name):
    if name == "before":
        return data.points[: data.samples]
    return np.load(OUT / f"{name}-{data.item.id}.npz")["samples"][:, :3]


def run():
    f = fixture(GeometryEngine())
    lib = library()
    lib.scm_surface_contacts.argtypes = [c.c_void_p, D, c.c_int, c.POINTER(c.c_int)]
    result = dict(
        before=captured(f.before, f.curves, lib, True), after=captured(f.after, f.curves, lib)
    )
    write("all-segment-contacts", result)
    print(result, flush=True)


if __name__ == "__main__":
    run()
