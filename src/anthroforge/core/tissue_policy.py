"""Construction capabilities own tissue eligibility, independent of anatomy labels."""

from collections.abc import Mapping

from .fibers import Fiber
from .membranes import Membrane
from .points import Anchor
from .tissues import TissueVCP


def domain(source: object) -> str:
    if isinstance(source, Anchor):
        return "POINT"
    if isinstance(source, Fiber):
        return "CURVE"
    if isinstance(source, Membrane):
        return "SURFACE"
    raise ValueError("Tissue construction requires an Anchor, Fiber or Membrane.")


def inflation_modes(source: object) -> frozenset[str]:
    kind = domain(source)
    if kind != "SURFACE":
        return frozenset(("RADIAL" if kind == "POINT" else "PROFILE",))
    modes = {"NORMAL"}
    if isinstance(source, Membrane) and source.kind != "PATCH":
        modes.update(("CTRL_POINT", "DISTRIBUTED"))
    if isinstance(source, Membrane) and source.kind == "LOFT" and not source.close_across:
        modes.add("SECTION_PROFILE")
    return frozenset(modes)


def validate(tissue: TissueVCP, records: Mapping[str, object]) -> None:
    source = records.get(tissue.source)
    modes = inflation_modes(source)
    validate_strategies(tissue, source)
    for part in tissue.parts:
        for side in (part.a, part.b) if tissue.both_sides else (part.a,):
            if side.inflation.mode not in modes:
                raise ValueError(f"{side.inflation.mode} is unsupported for this tissue source.")
    if tissue.stacking and domain(source) != "SURFACE":
        raise ValueError("Stacking currently requires surface-based tissue participants.")
    validate_surface(tissue, source, records)


def validate_surface(tissue: TissueVCP, source: object, records: Mapping[str, object]) -> None:
    if tissue.both_sides and not isinstance(source, Membrane):
        raise ValueError("Two-sided tissue requires a compatible membrane.")
    if not isinstance(source, Membrane):
        return
    closed = any(isinstance(c := records.get(u.curve), Fiber) and c.closed for u in source.curves)
    if tissue.both_sides and (closed or source.close_across):
        raise ValueError("Two-sided tissue requires open material axes.")
    validate_surface_modes(tissue, source, closed)


def validate_surface_modes(tissue: TissueVCP, source: Membrane, closed: bool) -> None:
    modes = {
        s.inflation.mode
        for p in tissue.parts
        for s in ((p.a, p.b) if tissue.both_sides else (p.a,))
    }
    if tissue.both_sides and modes & {"NORMAL", "RADIAL", "PROFILE"}:
        raise ValueError(
            "Two-sided composition requires muscle grid inflation; normal shells own their backing."
        )
    if "SECTION_PROFILE" in modes and (closed or source.kind != "LOFT" or source.close_across):
        raise ValueError("Section Profile requires an ordinary open loft.")


def sources(item: object) -> tuple[str, ...]:
    return (item.source,) if isinstance(item, TissueVCP) else ()


def region_masks(tissue: TissueVCP) -> tuple[str, ...]:
    mode = tissue.parts[0].a.inflation.mode
    groups = {
        "RADIAL": (),
        "PROFILE": ("BACKING", "ENDPOINTS"),
        "NORMAL": ("BACKING", "BOUNDARY", "SUSPENSION"),
    }
    return (
        "ALL",
        *groups.get(mode, ("BOUNDARY",)),
        *(f.name for f in tissue.fields if f.name != "INFLATION"),
    )


def validate_strategies(tissue: TissueVCP, source: object) -> None:
    modes = {p.a.inflation.mode for p in tissue.parts}
    if tissue.relaxation.mode != "NONE" and modes - {"RADIAL", "PROFILE", "NORMAL"}:
        raise ValueError(
            "Relaxation requires radial, profile or normal inflation; "
            "muscle grid modes retain height smoothing."
        )
    masks = region_masks(tissue)
    if any(r.mask not in masks for r in tissue.constraints):
        raise ValueError("Constraint mask unavailable; choose a supported region or custom field.")
    validate_fields(tissue, modes)


def validate_fields(tissue: TissueVCP, modes: set[str]) -> None:
    for field in tissue.fields:
        if field.name == "INFLATION" and (field.domain != "BASE" or modes != {"NORMAL"}):
            raise ValueError("The inflation field requires the Base domain of normal-shell tissue.")
        if not field.values:
            raise ValueError(
                "A custom tissue field needs explicit weights, including explicit zeros."
            )
