"""Accepted tissue capability selects proximity inputs; numerical weighting stays native."""

from dataclasses import dataclass
from typing import Any

from anthroforge.native import skin_ownership, skin_proximity


@dataclass(frozen=True)
class Adjustment:
    lengths: Any
    statistics: dict[str, Any]
    warnings: tuple[str, ...] = ()
    active: bool = False


def eligible(document: Any, source: Any) -> bool:
    if source.kind != "TISSUE":
        return False
    state = document.object(source.owner).rest_material
    return bool(state is not None and state.base_state.kind == "SURFACE")


def apply(
    document: Any, captured: Any, support: Any, mesh: Any, lengths: Any, cancel: int
) -> Adjustment:
    if document.skin.topology_settings.refinement == "NONE":
        return Adjustment(lengths, {})
    data = skin_ownership.pack(
        captured.geometry, support.offsets, support.bones, support.candidates
    )
    flags = [eligible(document, row.identity) for row in captured.sources]
    result = skin_proximity.evaluate(mesh, data, flags, lengths, cancel)
    return adjustment(result)


def adjustment(result: skin_proximity.Result) -> Adjustment:
    stats = statistics(result.statistics)
    warnings: tuple[str, ...] = ()
    if not stats["tissue_vertices"]:
        warnings = (
            "Proximity refinement found no accepted surface tissues; using uniform density.",
        )
    return Adjustment(result.lengths, stats, warnings, bool(stats["tissue_vertices"]))


def statistics(values: Any) -> dict[str, Any]:
    return dict(
        tissue_vertices=int(values[0]),
        influenced_skin_vertices=int(values[1]),
        influence_inner=float(values[2]),
        influence_outer=float(values[3]),
        maximum_density_multiplier=float(values[4]),
    )
