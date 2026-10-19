"""Native stack preparation fixtures retain real material layouts and typed configuration."""

from dataclasses import replace

import numpy as np

from anthroforge.core.tissue_base import TissueBaseState
from anthroforge.core.tissue_settings import TissuePart, TissueSide
from anthroforge.core.tissues import TissueVCP
from anthroforge.native import tissue_crop, tissue_parts
from anthroforge.native.tissue_stacking import MaterialLease


def item(parts, **options):
    parts = (replace(parts[0], id="main"), *parts[1:])
    return TissueVCP(
        name="Tissue",
        source="membrane",
        parts=parts,
        base_state=TissueBaseState("SURFACE", parts=tuple(p.id for p in parts)),
        **options,
    )


def ordinary(settings, **options):
    return item((TissuePart(a=TissueSide(settings)),), **options)


def arrays(domain):
    if not domain.vertices:
        return {name: np.empty((0, 3)) for name in ("base", "own", "direction", "faces")}
    result = {
        key: np.ctypeslib.as_array(getattr(domain, key), (domain.vertices * 3,)).reshape(-1, 3)
        for key in ("base", "own", "direction")
    }
    result["faces"] = np.ctypeslib.as_array(domain.faces, (domain.triangles * 3,)).reshape(-1, 3)
    return result


def leases(base, config):
    a = tissue_parts.evaluate(base, config.parts, "a", config.reverse, envelope=config.both_sides)
    rest = a
    if config.both_sides:
        b = tissue_parts.evaluate(base, config.parts, "b", not config.reverse, envelope=True)
        rest = tissue_parts.compose(a, b, config.reverse)
    own = tissue_crop.evaluate(base, rest, config.crop) if config.crop.enabled else rest
    first = MaterialLease(base, rest, own, config)
    second = MaterialLease(base, rest, own, config, side="b") if config.both_sides else None
    return own, first, second
