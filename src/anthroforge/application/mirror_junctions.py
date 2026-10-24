"""Shared junction identities are derived once per source junction and reflection rule."""

from typing import Any

from anthroforge.core.mirroring import MirrorInstance


def describe(document: Any, instance: Any) -> list[dict[str, Any]]:
    return [
        dict(
            id=MirrorInstance(key, instance.rule).id,
            source=key,
            members=[member(document, ref, instance.rule) for ref in refs],
        )
        for key, refs in document.mirrors.junctions.get(instance.source, ())
    ]


def member(document: Any, ref: Any, rule: str) -> dict[str, Any]:
    target = MirrorInstance(ref.curve, rule).id
    item = document.object(ref.curve)
    complete = complete_seam(document, item, ref.point, rule)
    return dict(
        curve=ref.curve,
        point=ref.point,
        instance=ref.curve if complete else target,
        available=complete or target in document.mirrors.instances,
    )


def complete_seam(document: Any, item: Any, point: str, rule: str) -> bool:
    from .symmetric_paths import plane

    if not item.symmetric or point not in (item.points[0].id, item.points[-1].id):
        return False
    original, mirrored = plane(document, item.symmetric), document.mirrors.rules[rule]
    return bool(original.axis == mirrored.axis and original.shift == mirrored.shift)
