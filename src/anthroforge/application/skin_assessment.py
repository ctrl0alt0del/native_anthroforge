"""Read-only metadata assessments; geometry compatibility stays on coordinator workers."""

import json
from typing import Any

from anthroforge.core import skin_sources
from anthroforge.core.entities import SCP
from anthroforge.core.results import Port, geometry_asset
from anthroforge.core.skin_pipeline import Assessment, Condition, Inputs

from . import skin_inputs, skin_status, skin_update_tasks
from .construction_policy import revisions


def assess(document: Any, resources: Any) -> Inputs:
    return Inputs(
        sources(document, resources),
        draft(document, resources),
        topology(document, resources),
        reference(document, resources),
        final_current(document, resources),
    )


def final_current(document: Any, resources: Any) -> bool:
    skin = document.skin
    data = resources.skin.get(skin.final.data)
    if data is None or json.loads(data.metadata).get("reference") != skin.reference:
        return False
    ports = skin_update_tasks.inputs(resources, document) - {
        Port(str(document.id), "skin_reference")
    }
    return current(document, skin.final, ports)


def current(document: Any, stage: Any, ports: set[Port]) -> bool:
    if not stage.asset or stage.pending or stage.status != "ready":
        return False
    reads = {Port(r.owner, r.output): r for r in stage.inputs}
    try:
        return all(reads.get(Port(r.owner, r.output)) == r for r in revisions(document, ports))
    except (KeyError, ValueError):
        return False


def draft(document: Any, resources: Any) -> Assessment:
    if reason := skin_status.draft_reason(document):
        return Assessment(Condition.UNAVAILABLE, reason)
    stage = document.skin.envelope
    if stage.asset not in resources.meshes or stage.data not in resources.skin:
        return Assessment(Condition.MISSING, "Draft skin is required.")
    if not current(document, stage, skin_inputs.envelope(document)):
        return Assessment(Condition.STALE, "Draft skin needs the committed anatomy.")
    return Assessment()


def membership(document: Any, data: Any) -> bool:
    info = json.loads(data.metadata)
    if "sources" not in info:
        return False
    rows = tuple((r["owner"], r["kind"], r["instance"]) for r in info["sources"])
    return rows == tuple((r.owner, r.kind, r.instance) for r in skin_sources.contributors(document))


def topology(document: Any, resources: Any) -> Assessment:
    skin = document.skin
    stage = skin.pending_topology if skin.pending_topology.asset else skin.topology
    data = resources.skin.get(stage.data)
    if stage.asset not in resources.meshes or data is None:
        return Assessment(Condition.MISSING, "Skin topology is required.")
    if not membership(document, data):
        return Assessment(Condition.INCOMPATIBLE, "Topology contributor identities changed.")
    if skin.pending_topology.asset and skin_status.pending_reason(document):
        return Assessment(Condition.STALE, "Retained topology needs current anatomy.")
    return Assessment()


def reference(document: Any, resources: Any) -> Assessment:
    skin = document.skin
    data = resources.skin.get(skin.reference)
    if data is None or skin.final.asset not in resources.meshes:
        return Assessment(Condition.MISSING, "A deformation reference is required.")
    if not membership(document, data):
        return Assessment(Condition.INCOMPATIBLE, "Reference contributor identities changed.")
    if set(skin.reference_sources) - resources.meshes.keys():
        return Assessment(Condition.INCOMPATIBLE, "Retained anatomical material is unavailable.")
    if resources.meshes[skin.final.asset].mesh.counts[0] != len(data.arrays["vertex_ids"]):
        return Assessment(Condition.MISSING, "Skin vertex identities need a new reference.")
    return Assessment()


def sources(document: Any, resources: Any) -> Assessment:
    rows = skin_sources.contributors(document)
    if not rows:
        return Assessment(Condition.EMPTY, "No physical anatomy contributors.")
    for row in rows:
        state = source(document.object(row.owner), resources)
        if state.condition != Condition.READY:
            return state
    return Assessment()


def source(item: Any, resources: Any) -> Assessment:
    result = item.result if isinstance(item, SCP) else item.final_result
    error = result.error or (item.error if isinstance(item, SCP) else "")
    if error or result.status in ("failed", "invalid", "cancelled"):
        return Assessment(Condition.FAILED, f"{item.name}: {error or result.status}")
    pending_pose = isinstance(item, SCP) and bool(item.parent) and item.status != "ready"
    if result.status == "pending" or pending_pose or geometry_asset(item) not in resources.meshes:
        return Assessment(Condition.WAITING, f"Waiting for {item.name}.")
    return Assessment()
