"""Persist mirror relationships only; source assets remain the single geometry owner."""

from typing import Any

from anthroforge.core.mirror_resolution import MirrorIndex
from anthroforge.core.mirroring import MirrorInstance, MirrorRule, SharedMirrorTarget


def fields(data: dict[str, Any]) -> dict[str, Any]:
    return dict(
        mirror_rules=tuple(rule(v) for v in data.get("mirror_rules", ())),
        shared_mirror_targets=tuple(
            SharedMirrorTarget(**v) for v in data.get("shared_mirror_targets", ())
        ),
        _mirrors=accepted(data),
    )


def accepted(data: dict[str, Any]) -> MirrorIndex | None:
    values = data.get("mirror_accepted", ())
    if not values:
        return None
    instances = [MirrorInstance(v["source"], v["rule"]) for v in values]
    rules = {v["target"]: rule(v) for v in data.get("mirror_rules", ())}
    placements = {
        i.id: MirrorRule(i.rule, axis=v["axis"], shift=v["shift"])
        for i, v in zip(instances, values, strict=True)
    }
    return MirrorIndex(("restored",), {i.id: i for i in instances}, rules, placements=placements)


def rule(value: Any) -> MirrorRule:
    return MirrorRule(**dict(value, scope=tuple(value.get("scope", ()))))


def snapshot(document: Any) -> list[dict[str, Any]]:
    return [
        dict(
            source=v.source,
            rule=v.rule,
            axis=document.mirrors.plane(v).axis,
            shift=document.mirrors.plane(v).shift,
        )
        for v in document.mirrors.instances.values()
    ]
