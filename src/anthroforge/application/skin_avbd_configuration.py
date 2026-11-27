"""AVBD-only route, input and configuration policies."""

import json
from dataclasses import replace
from typing import Any

from anthroforge.core import anatomical_surfaces, skin_avbd_settings, skin_sources
from anthroforge.core.skin_limb import SkinLimb
from anthroforge.core.surface_references import SurfaceReference

FIELDS = frozenset(skin_avbd_settings.AvbdContributor.__dataclass_fields__) - {"owner"}


def configure(config: Any, values: dict[str, Any]) -> Any:
    values = dict(values)
    if isinstance(values.get("plan"), dict):
        values["plan"] = json.dumps(values["plan"], allow_nan=False)
    return replace(config, **values)


def contributor(config: Any, owner: str) -> Any:
    return next(
        (r for r in config.contributors if r.owner == owner),
        skin_avbd_settings.AvbdContributor(owner),
    )


def configure_contributor(config: Any, owner: str, values: dict[str, Any]) -> Any:
    current = contributor(config, owner)
    if isinstance(values.get("limb"), dict):
        values = values | {"limb": replace(current.limb or SkinLimb(), **values["limb"])}
    rows = {r.owner: r for r in config.contributors} | {owner: replace(current, **values)}
    return replace(config, contributors=tuple(rows.values()))


def inputs(document: Any) -> set[Any]:
    from .skin_inputs import source_ports

    sources = skin_sources.contributors(document)
    ports = set().union(*(source_ports(row) for row in sources))
    for row in sources:
        if row.kind == "TISSUE":
            ref = SurfaceReference(row.owner, "TISSUE_BASE", row.instance)
            ports.update(anatomical_surfaces.inputs(ref))
    return ports


def reason(document: Any) -> str:
    sources = skin_sources.contributors(document)
    if not any(s.kind == "SCP" for s in sources):
        return "AVBD draft construction needs an SCP root."
    for row in sources:
        if row.kind == "TISSUE":
            item = document.object(row.owner)
            if "TISSUE_BASE" not in anatomical_surfaces.roles(item, document.registry.records):
                return f"AVBD needs corresponding base and finished surfaces for {item.name}."
    return ""


def signature(document: Any) -> tuple[str, ...]:
    from anthroforge.core.tissues import TissueVCP

    tree = [(e.id, e.parent, e.attachment) for e in document.entities]
    tissues = [o.id for o in document.objects if isinstance(o, TissueVCP)]
    record = document.skin.draft_settings.configuration("AVBD")
    return tuple(map(repr, (record, tree, tissues)))
