"""One authored revision policy for generic construction objects."""

from dataclasses import fields, replace

from anthroforge.core.objects import ConstructionObject
from anthroforge.core.results import Port

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
    )
)


def changed_ports(before: ConstructionObject, after: ConstructionObject) -> set[Port]:
    names = {f.name for f in fields(after) if getattr(before, f.name) != getattr(after, f.name)}
    result = {Port(after.id, "local_pose")} if names & POSE else set()
    if names - POSE - METADATA:
        from anthroforge.core.construction import Curve

        result.add(Port(after.id, "path" if isinstance(after, Curve) else "geometry"))
    return result


def authored[T: ConstructionObject](before: T, after: T) -> T:
    if after == before:
        return before
    ports = changed_ports(before, after)
    return replace(
        after,
        generation=before.generation + 1,
        pose_revision=before.pose_revision + int(Port(after.id, "local_pose") in ports),
        construction_revision=before.construction_revision
        + int(any(p.output != "local_pose" for p in ports)),
    )
