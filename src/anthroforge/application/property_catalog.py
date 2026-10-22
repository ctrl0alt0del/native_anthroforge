"""Discover authored numerical properties through explicit semantic roots."""

from collections.abc import Iterator
from dataclasses import fields, is_dataclass, replace
from typing import Any

from anthroforge.core import numeric_properties as numeric
from anthroforge.core.construction import Control, Curve
from anthroforge.core.entities import SCP
from anthroforge.core.points import Point
from anthroforge.core.reference_images import ReferenceImage
from anthroforge.core.surfaces import Surface
from anthroforge.core.tissues import TissueVCP

ROOTS = {
    SCP: ("geometry_offset", "primitive", "deformers", "thickness"),
    Curve: ("points", "engine_settings", "start", "span"),
    Control: ("resolution", "weights", "deformers"),
    Point: ("position",),
    Surface: ("curves", "strips", "patch_resolution", "branches"),
    ReferenceImage: ("width",),
    TissueVCP: ("parts", "resolution", "relaxation", "crop", "constraints", "stack_settings"),
}
EXCLUDED = frozenset(("bind", "matrix", "indices", "members", "stations", "result", "revision"))
DIMENSIONS = {
    "SCP": {"geometry_offset": "LENGTH"},
    "CurvePoint": {"position": "LENGTH", "left": "LENGTH", "right": "LENGTH", "tilt": "ANGLE"},
    "BodyPiece": dict.fromkeys(("width", "depth", "length", "position"), "LENGTH"),
    "Deformer": dict.fromkeys(("center", "radius", "displacement"), "LENGTH"),
    "Thickness": {"thickness": "LENGTH"},
    "RoutingSettings": {"radius": "LENGTH"},
    "Point": {"position": "LENGTH"},
    "Anchor": {"position": "LENGTH"},
    "ReferenceImage": {"width": "LENGTH"},
    "TissueInflation": dict.fromkeys(
        (
            "amount",
            "minimum",
            "width",
            "falloff_radius",
            "direction_depth",
            "boundary_band",
            "length_taper",
            "control",
        ),
        "LENGTH",
    ),
    "SectionProfile": {"depths": "LENGTH"},
    "HeightSmoothing": dict.fromkeys(("radius", "maximum_change"), "LENGTH"),
    "TissueRelaxation": {"sag_limit": "LENGTH", "tolerance": "LENGTH"},
    "TissueCrop": {"origin": "LENGTH"},
}


def roots(item: Any) -> tuple[str, ...]:
    for kind, names in ROOTS.items():
        if isinstance(item, kind):
            return names
    return ()


def descriptors(item: Any) -> Iterator[numeric.NumericDescriptor]:
    for name in roots(item):
        if hasattr(item, name):
            yield from walk(item.id, getattr(item, name), (name,), dimension(item, name))


def dimension(owner: Any, name: str) -> str:
    return DIMENSIONS.get(type(owner).__name__, {}).get(name, "SCALAR")


def walk(target: str, value: Any, path: tuple[str, ...], unit: str) -> Iterator[Any]:
    if type(value) in (int, float) or numeric_vector(value):
        yield descriptor(target, path, value, unit)
    elif is_dataclass(value):
        for field in fields(value):
            if field.name not in EXCLUDED:
                child = getattr(value, field.name)
                yield from walk(target, child, (*path, field.name), dimension(value, field.name))
    elif isinstance(value, tuple):
        for child in value:
            if hasattr(child, "id"):
                yield from walk(target, child, (*path, "@" + child.id), "SCALAR")


def numeric_vector(value: Any) -> bool:
    return isinstance(value, tuple) and bool(value) and all(type(v) in (int, float) for v in value)


def descriptor(
    target: str, path: tuple[str, ...], value: Any, unit: str
) -> numeric.NumericDescriptor:
    values = value if isinstance(value, tuple) else (value,)
    kind = "INTEGER" if all(type(v) is int for v in values) else "REAL"
    label = " / ".join(p.replace("_", " ").title() for p in path if not p.startswith("@"))
    return numeric.NumericDescriptor(
        numeric.PropertyRef(target, path), label, kind, unit, len(values)
    )


def resolve(document: Any, reference: numeric.PropertyRef) -> numeric.NumericDescriptor:
    item = document.object(reference.target)
    for candidate in descriptors(item):
        if candidate.reference.path == reference.path:
            if reference.component is not None and reference.component >= candidate.components:
                raise ValueError("Numerical property component is unavailable.")
            return replace(candidate, reference=reference)
    raise ValueError("This is not an eligible numerical property.")
