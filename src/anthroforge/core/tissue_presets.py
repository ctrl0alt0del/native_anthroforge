"""Creation defaults from the addon; classification never dispatches an evaluator."""

from typing import Any

from .membranes import Membrane
from .tissue_constraints import TissueConstraint
from .tissue_policy import domain
from .tissue_settings import TissueInflation, TissuePart, TissueRelaxation, TissueSide

PresetValues = tuple[str, str, dict[str, Any], dict[str, Any], tuple[tuple[str, str, float], ...]]
PRESETS: dict[str, PresetValues] = {
    "MUSCLE": ("Muscle", "", {}, {}, ()),
    "CUSTOM": ("Custom", "", {}, {}, ()),
    "CLOSED_BULK": (
        "Closed bulk",
        "POINT",
        dict(amount=0.2),
        dict(
            mode="GEOMETRIC",
            sagginess=0.035,
            sag_limit=0.35,
            shape_retention=0.25,
            volume_retention=0.9,
            iterations=20,
            constraint_passes=1,
        ),
        (),
    ),
    "RIM": (
        "Rim",
        "CURVE",
        dict(amount=0.12, width=0.08, power=0.65, segments=11, endpoint_taper=0.12),
        dict(
            mode="GEOMETRIC",
            sagginess=0.08,
            sag_limit=0.024,
            shape_retention=0.72,
            volume_retention=0.92,
        ),
        (("BACKING", "FIXED", 1.0), ("ENDPOINTS", "FIXED", 1.0)),
    ),
    "LAYER": (
        "Layer",
        "SURFACE",
        dict(amount=0.28, minimum=0.008, power=0.78),
        dict(
            mode="GEOMETRIC",
            sagginess=0.65,
            sag_limit=0.2,
            shape_retention=0.48,
            volume_retention=0.88,
            iterations=100,
            constraint_passes=4,
        ),
        (("BOUNDARY", "FIXED", 1.0), ("BACKING", "SOFT", 0.55)),
    ),
    "POUCH": (
        "Pouch",
        "SURFACE",
        dict(amount=0.62, minimum=0.012, power=0.58),
        dict(
            mode="STATIC_PBD",
            sagginess=0.58,
            shape_retention=0.48,
            volume_retention=0.88,
            iterations=110,
            constraint_passes=4,
        ),
        (("BOUNDARY", "FIXED", 1.0), ("BACKING", "FIXED", 1.0)),
    ),
}


def available(source: object) -> list[dict[str, str]]:
    kind = domain(source)
    return [dict(id=key, name=row[0]) for key, row in PRESETS.items() if row[1] in ("", kind)]


def settings(source: object, preset: str) -> dict[str, Any]:
    if preset not in {row["id"] for row in available(source)}:
        raise ValueError("Choose a tissue preset compatible with the selected construction source.")
    _, _, inflation, relaxation, constraints = PRESETS[preset]
    side = TissueSide(TissueInflation(mode=mode(source, preset), **inflation))
    return dict(
        parts=(TissuePart(a=side, b=side),),
        relaxation=TissueRelaxation(**relaxation),
        constraints=tuple(TissueConstraint(mask=m, mode=k, strength=s) for m, k, s in constraints),
        resolution=33 if preset == "RIM" else 24,
        stacking=preset == "MUSCLE" and domain(source) == "SURFACE",
        classification="MUSCLE" if preset == "MUSCLE" else "SOFT_TISSUE",
    )


def mode(source: object, preset: str) -> str:
    if preset == "MUSCLE" and isinstance(source, Membrane) and source.kind != "PATCH":
        return "DISTRIBUTED"
    return {"POINT": "RADIAL", "CURVE": "PROFILE", "SURFACE": "NORMAL"}[domain(source)]
