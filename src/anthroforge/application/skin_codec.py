"""Editable skin records; accepted arrays are owned by resource storage."""

from typing import Any

from anthroforge.core.results import ReadRevision
from anthroforge.core.skin import (
    DeformationSettings,
    EnvelopeSettings,
    FittedShortcut,
    Skin,
    SkinContributor,
    SkinStage,
    TopologySettings,
)
from anthroforge.core.skin_draft import DraftSettings
from anthroforge.core.skin_limb import SkinLimb


def result(value: dict[str, Any]) -> SkinStage:
    reads = tuple(
        ReadRevision(**(row | {"membership": tuple(row.get("membership", ()))}))
        for row in value.get("inputs", ())
    )
    return SkinStage(**(value | {"inputs": reads, "pending": tuple(value.get("pending", ()))}))


def decode(value: dict[str, Any] | None) -> Skin:
    data = dict(value or {})
    data["reference_sources"] = tuple(data.get("reference_sources", ()))
    data["draft_settings"] = DraftSettings(**data.get("draft_settings", {}))
    data["envelope_settings"] = EnvelopeSettings(**data.get("envelope_settings", {}))
    data["deformation_settings"] = DeformationSettings(**data.get("deformation_settings", {}))
    data["topology_settings"] = decode_topology(data.get("topology_settings", {}))
    for name in ("envelope", "topology", "pending_topology", "final"):
        data[name] = result(data.get(name, {}))
    data["contributors"] = tuple(contributor(row) for row in data.get("contributors", ()))
    data["fits"] = tuple(fitted(row) for row in data.get("fits", ()))
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
    data.pop("fiber_radius", None)
    if data.get("limb") is not None:
        data["limb"] = SkinLimb(**data["limb"])
    return SkinContributor(**data)


def fitted(value: dict[str, Any]) -> FittedShortcut:
    reads = result({"inputs": value.get("inputs", ())}).inputs
    return FittedShortcut(**(value | {"inputs": reads}))
