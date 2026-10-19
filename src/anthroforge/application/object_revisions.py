"""One authored revision policy for generic construction objects."""

from dataclasses import fields, replace
from typing import Any

from anthroforge.core import tissue_revisions
from anthroforge.core.object_outputs import output
from anthroforge.core.objects import ObjectRecord
from anthroforge.core.results import Port
from anthroforge.core.tissues import TissueVCP

POSE = frozenset(("matrix", "parent"))
METADATA = frozenset(
    (
        "id",
        "name",
        "owners",
        "update_mode",
        "generation",
        "pose_revision",
        "construction_revision",
        "result",
        "base_result",
        "rest_result",
        "intrinsic_result",
        "final_result",
        "resolved_position",
        "resolved_frame",
    )
)


def changed_ports(before: ObjectRecord, after: ObjectRecord) -> set[Port]:
    names = {f.name for f in fields(after) if getattr(before, f.name) != getattr(after, f.name)}
    result = {Port(after.id, "local_pose")} if names & POSE else set()
    if isinstance(after, TissueVCP):
        return result | tissue_revisions.ports(after.id, names)
    if names - POSE - METADATA:
        result.add(Port(after.id, output(after)))
    return result


def authored[T: ObjectRecord](before: T, after: T) -> T:
    if after == before:
        return before
    ports = changed_ports(before, after)
    phases: dict[str, Any] = (
        tissue_revisions.changes(before, ports) if isinstance(before, TissueVCP) else {}
    )
    return replace(
        after,
        generation=before.generation + 1,
        pose_revision=before.pose_revision + int(Port(after.id, "local_pose") in ports),
        construction_revision=before.construction_revision
        + int(any(p.output != "local_pose" for p in ports)),
        **phases,
    )
