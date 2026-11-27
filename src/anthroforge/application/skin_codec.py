"""Editable skin records; accepted arrays are owned by resource storage."""

from typing import Any

from anthroforge.core.results import ReadRevision
from anthroforge.core.skin import (
    DeformationSettings,
    FittedShortcut,
    Skin,
    SkinContributor,
    SkinStage,
    TopologySettings,
)
from anthroforge.core.skin_checkpoints import Checkpoint

from . import skin_builder_codec


def result(value: dict[str, Any]) -> SkinStage:
    reads = tuple(
        ReadRevision(**(row | {"membership": tuple(row.get("membership", ()))}))
        for row in value.get("inputs", ())
    )
    return SkinStage(**(value | {"inputs": reads, "pending": tuple(value.get("pending", ()))}))


def decode(value: dict[str, Any] | None) -> Skin:
    data = dict(value or {})
    data["reference_sources"] = tuple(data.get("reference_sources", ()))
    data.update(skin_builder_codec.upgrade(data))
    data.pop("envelope_settings", None)
    data["deformation_settings"] = DeformationSettings(**data.get("deformation_settings", {}))
    data["topology_settings"] = decode_topology(data.get("topology_settings", {}))
    for name in ("envelope", "topology", "pending_topology", "final"):
        data[name] = result(data.get(name, {}))
    data["contributors"] = tuple(contributor(row) for row in data.get("contributors", ()))
    data["fits"] = tuple(fitted(row) for row in data.get("fits", ()))
    data["checkpoints"] = tuple(Checkpoint(**row) for row in data.get("checkpoints", ()))
    return Skin(**data)


def decode_topology(values: dict[str, Any]) -> TopologySettings:
    topology = dict(values)
    for name in ("plane_origin", "plane_normal"):
        if name in topology:
            topology[name] = tuple(topology[name])
    return TopologySettings(**topology)


def contributor(value: dict[str, Any]) -> SkinContributor:
    # Pre-release schema-7 snapshots may contain the superseded physical Fiber radius.
    data = dict(value)
    from .skin_avbd_configuration import FIELDS as AVBD_FIELDS
    from .skin_field_configuration import FIELDS as FIELD_FIELDS

    for name in AVBD_FIELDS | FIELD_FIELDS | {"fiber_radius"}:
        data.pop(name, None)
    return SkinContributor(**data)


def fitted(value: dict[str, Any]) -> FittedShortcut:
    reads = result({"inputs": value.get("inputs", ())}).inputs
    return FittedShortcut(**(value | {"inputs": reads}))
