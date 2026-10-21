"""Shared validated stacking settings, persistent intent and relationship inspection."""

from dataclasses import asdict, replace
from typing import Any

from anthroforge.core.tissue_stacking import StackRelationship, StackSettings
from anthroforge.core.tissues import TissueVCP

from . import object_operations, tissue_fields
from .tissue_operations import tissue
from .tissue_strategy_operations import install


def configure(session: Any, target: str, changes: dict[str, Any]) -> None:
    item = tissue(session, target)
    if set(changes) - set(StackSettings.__dataclass_fields__):
        raise ValueError("Unknown stacking setting.")
    install(session, replace(item, stack_settings=replace(item.stack_settings, **changes)))


def relationship(session: Any, target: str, other: str, **settings: Any) -> None:
    item, provider = tissue(session, target), session.document.object(other)
    if not isinstance(provider, TissueVCP) or provider.id == item.id:
        raise ValueError("Choose a different surface tissue for the relationship.")
    data = relationship_data(session, item, provider, settings)
    row = StackRelationship(other, **data)
    require_available(item, provider, row)
    existing = tuple(r for r in item.stack_relationships if pair(r) != pair(row))
    install(session, replace(item, stack_relationships=(*existing, row)))


def relationship_data(session: Any, item: Any, provider: Any, settings: Any) -> dict[str, Any]:
    key = (provider.id, settings.get("side", "a"), settings.get("other_side", "a"))
    previous = next((r for r in item.stack_relationships if pair(r) == key), None)
    data = asdict(previous) if previous else {}
    data.pop("other", None)
    data.update(settings)
    if "regions" in settings:
        capture_regions(session, item, provider, data, settings.get("topology", ""))
    elif previous and previous.regions and previous.cover != data.get("cover", "SELF"):
        raise ValueError("Select a new support region when changing the covering tissue.")
    return data


def capture_regions(session: Any, item: Any, provider: Any, data: Any, expected: str) -> None:
    from anthroforge.native import tissue_regions

    cover = item if data.get("cover", "SELF") == "SELF" else provider
    topology = tissue_fields.domain(session.resources, cover, "BASE")[1]
    if expected and expected != topology:
        raise ValueError("Support material topology changed; select the region again.")
    regions = tuple(tuple(row) for row in data["regions"])
    parts = {key: i for i, key in enumerate(cover.base_state.parts)}
    if any(part not in parts for part, _ in regions):
        raise ValueError("Support selection refers to an unavailable construction part.")
    side = data.get("side", "a") if cover.id == item.id else data.get("other_side", "a")
    mesh = session.assets[cover.rest_result.asset].mesh
    tissue_regions.validate(mesh, [(parts[p], f) for p, f in regions], side)
    data.update(regions=regions, topology=topology)


def pair(row: StackRelationship) -> tuple[str, str, str]:
    return row.other, row.side, row.other_side


def require_available(item: TissueVCP, other: TissueVCP, row: StackRelationship) -> None:
    if any(o.base_state.kind != "SURFACE" for o in (item, other)):
        raise ValueError("Both participants require accepted surface construction.")
    if (row.side == "b" and not item.both_sides) or (
        row.other_side == "b" and not other.both_sides
    ):
        raise ValueError("The selected tissue has no second inflation side.")
    for previous in other.stack_relationships:
        if pair(previous) == (item.id, row.other_side, row.side):
            raise ValueError(
                "This relationship is owned by " + other.name + "; edit or remove it there."
            )


def remove(session: Any, target: str, other: str, side: str = "a", other_side: str = "a") -> None:
    item = tissue(session, target)
    rows = tuple(r for r in item.stack_relationships if pair(r) != (other, side, other_side))
    if rows == item.stack_relationships:
        raise ValueError("No saved relationship exists for this side pair.")
    object_operations.install(session, replace(item, stack_relationships=rows))


def inspect(session: Any, target: str) -> dict[str, Any]:
    item = session.document.object(target)
    if not isinstance(item, TissueVCP):
        raise ValueError("Select a tissue to inspect stacking.")
    return dict(
        group=item.group,
        settings=asdict(item.stack_settings),
        intent=[asdict(r) for r in item.stack_relationships],
        plan=asdict(item.stack_plan),
        state=item.final_result.status,
        error=item.final_result.error,
    )
