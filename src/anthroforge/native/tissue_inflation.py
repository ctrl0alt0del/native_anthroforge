"""Batched settings adapter for native tissue inflation; no Python numerical evaluation."""

import ctypes as c

from anthroforge.core.tissue_settings import TissueInflation

from .mesh import D, GeometryEngine, Mesh, U, doubles, pointer


class Inflation(c.Structure):
    _fields_ = [
        (name, c.c_int)
        for name in ("mode", "enabled", "reverse", "falloff", "direction", "initialize_control")
    ]
    _fields_ += [
        (name, c.c_double)
        for name in (
            "amount",
            "radius",
            "depth",
            "boundary_strength",
            "boundary_band",
            "boundary_power",
            "taper",
        )
    ]
    _fields_ += [("control", c.c_double * 3), ("profile", c.c_double * 9)]


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_tissue_inflate_grid", [U, c.POINTER(Inflation), c.c_int, U], U)
    engine.bind("af_tissue_source_mesh", [U, D, U], U)
    engine.bind("af_tissue_refine_grid", [U, c.c_int, U], U)


def pack(settings: TissueInflation, reverse: bool = False) -> Inflation:
    mode = ("CTRL_POINT", "DISTRIBUTED", "SECTION_PROFILE").index(settings.mode)
    direction = ("LOCAL", "SMOOTH", "SECTION").index(settings.profile.direction)
    falloff = {"GAUSSIAN": 0, "LINEAR": 1, "SMOOTH": 2, "SMOOTHSTEP": 2}[settings.falloff]
    flags = (mode, settings.enabled, reverse, falloff, direction, not settings.control)
    result = Inflation(*flags, *scalars(settings))
    result.control[:] = settings.control or (0, 0, 0)
    result.profile[:] = (
        *settings.profile.depths,
        *settings.profile.peaks,
        settings.profile.roundness,
    )
    return result


def scalars(settings: TissueInflation) -> tuple[float, ...]:
    return (
        settings.amount,
        settings.falloff_radius,
        settings.direction_depth,
        settings.boundary_strength,
        settings.boundary_band,
        settings.boundary_power,
        settings.length_taper,
    )


def evaluate(mesh: Mesh, settings: TissueInflation, reverse: bool = False, cancel: int = 0) -> Mesh:
    packed = pack(settings, reverse)
    handle = mesh.engine.library.af_tissue_inflate_grid(mesh.handle, c.byref(packed), 1, cancel)
    mesh.engine.check(not handle)
    return Mesh(mesh.engine, handle)


def source(mesh: Mesh, frame: tuple[float, ...], cancel: int = 0) -> Mesh:
    values = doubles(frame)
    handle = mesh.engine.library.af_tissue_source_mesh(mesh.handle, pointer(values), cancel)
    mesh.engine.check(not handle)
    return Mesh(mesh.engine, handle)


def refine(mesh: Mesh, resolution: int, cancel: int = 0) -> Mesh:
    handle = mesh.engine.library.af_tissue_refine_grid(mesh.handle, resolution, cancel)
    mesh.engine.check(not handle)
    return Mesh(mesh.engine, handle)
