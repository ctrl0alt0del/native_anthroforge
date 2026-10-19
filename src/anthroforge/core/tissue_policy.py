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
    for part in tissue.parts:
        for side in (part.a, part.b) if tissue.both_sides else (part.a,):
            if side.inflation.mode not in modes:
                raise ValueError(f"{side.inflation.mode} is unsupported for this tissue source.")
    if tissue.stacking and domain(source) != "SURFACE":
        raise ValueError("Stacking currently requires surface-based tissue participants.")
    if tissue.both_sides and not isinstance(source, Membrane):
        raise ValueError("Two-sided tissue requires a compatible membrane.")
    validate_surface(tissue, source, records)


def validate_surface(tissue: TissueVCP, source: object, records: Mapping[str, object]) -> None:
    if not isinstance(source, Membrane):
        return
    closed = any(isinstance(c := records.get(u.curve), Fiber) and c.closed for u in source.curves)
    if tissue.both_sides and (closed or source.close_across):
        raise ValueError("Two-sided tissue requires open material axes.")
    modes = {
        s.inflation.mode
        for p in tissue.parts
        for s in ((p.a, p.b) if tissue.both_sides else (p.a,))
    }
    if "SECTION_PROFILE" in modes and (closed or source.kind != "LOFT" or source.close_across):
        raise ValueError("Section Profile requires an ordinary open loft.")


def sources(item: object) -> tuple[str, ...]:
    return (item.source,) if isinstance(item, TissueVCP) else ()
