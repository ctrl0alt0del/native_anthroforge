"""Mapped mirror relationships are inspected, never used to deform the instance."""

from dataclasses import asdict, replace
from typing import Any

from anthroforge.core.entities import SCP
from anthroforge.core.fibers import Fiber
from anthroforge.core.mirroring import MirrorInstance, SharedMirrorTarget
from anthroforge.core.points import Anchor
from anthroforge.core.surface_references import SurfaceReference


def references(item: Any) -> tuple[tuple[str, SurfaceReference], ...]:
    if isinstance(item, Fiber):
        return tuple((b.point, b.reference) for b in item.bindings)
    if isinstance(item, Anchor):
        return (("binding", item.binding.reference),)
    if isinstance(item, SCP) and item.parent:
        return (
            ("attachment", SurfaceReference(item.parent, instance=item.attachment.parent_instance)),
        )
    return ()


def counterpart(document: Any, instance: Any, key: str, ref: SurfaceReference) -> SurfaceReference:
    if SharedMirrorTarget(instance.source, key) in document.shared_mirror_targets:
        return ref
    if ref.instance:
        if ref.instance != instance.rule:
            raise ValueError("Attachment and mirror use incompatible reflection rules.")
        return replace(ref, instance="")
    identity = MirrorInstance(ref.target, instance.rule).id
    if identity not in document.mirrors.instances:
        raise ValueError(
            "Attachment target has no mirrored counterpart; choose explicit midline sharing."
        )
    return replace(ref, instance=instance.rule)


def inspect(session: Any, target: str) -> list[dict[str, Any]]:
    from .inspection_context import freeze
    from .mirror_attachment_checks import validate

    document = session.document
    if target not in document.mirrors.instances:
        raise ValueError("Choose an existing mirrored instance.")
    instance = document.mirrors.instances[target]
    return validate(freeze(session), instance, rows(document, instance))


def rows(document: Any, instance: Any) -> list[dict[str, Any]]:
    result = []
    for key, ref in references(document.object(instance.source)):
        row = dict(binding=key, reference=asdict(ref), source=instance.source, instance=instance.id)
        try:
            row.update(mapped=asdict(counterpart(document, instance, key, ref)), status="mapped")
        except ValueError as error:
            row.update(mapped=None, status="missing", error=str(error))
        result.append(row)
    return result
