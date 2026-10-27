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


def result(value: dict[str, Any]) -> SkinStage:
    reads = tuple(
        ReadRevision(**(row | {"membership": tuple(row.get("membership", ()))}))
        for row in value.get("inputs", ())
    )
    return SkinStage(**(value | {"inputs": reads, "pending": tuple(value.get("pending", ()))}))


def decode(value: dict[str, Any] | None) -> Skin:
    data = dict(value or {})
    data["reference_sources"] = tuple(data.get("reference_sources", ()))
    data["envelope_settings"] = EnvelopeSettings(**data.get("envelope_settings", {}))
    data["deformation_settings"] = DeformationSettings(**data.get("deformation_settings", {}))
    topology = dict(data.get("topology_settings", {}))
    for name in ("plane_origin", "plane_normal"):
        if name in topology:
            topology[name] = tuple(topology[name])
    data["topology_settings"] = TopologySettings(**topology)
    for name in ("envelope", "topology", "pending_topology", "final"):
        data[name] = result(data.get(name, {}))
    data["contributors"] = tuple(contributor(row) for row in data.get("contributors", ()))
    data["fits"] = tuple(FittedShortcut(**row) for row in data.get("fits", ()))
    return Skin(**data)


def contributor(value: dict[str, Any]) -> SkinContributor:
    # Pre-release schema-7 snapshots may contain the superseded physical Fiber radius.
    data = dict(value)
    data.pop("fiber_radius", None)
    return SkinContributor(**data)
