"""SCP structural parents remain authored identities; attachment targets name an instance."""

from typing import Any

from anthroforge.core.mirroring import MirrorInstance, parse
from anthroforge.core.document import Document


def selected(document: Any, target: str) -> tuple[str, str]:
    instance = parse(target)
    if not instance:
        return target, ""
    if target not in document.mirrors.instances or instance.source not in document.index.entities:
        raise ValueError("Choose an existing mirrored SCP parent.")
    return instance.source, instance.rule


def frame(document: Document, item: Any) -> tuple[float, ...]:
    rule = item.attachment.parent_instance
    if MirrorInstance(item.parent, rule).id not in document.mirrors.instances:
        raise ValueError("The parent attachment's mirrored instance is unavailable.")
    return document.mirrors.rules[rule].frame


def reflections(document: Any, targets: set[str]) -> dict[str, tuple[float, ...]]:
    return {key: frame(document, document.entity(key)) for key in targets
            if document.entity(key).attachment.parent_instance}


def receipt(document: Any, child: Any, parent: Any) -> Any:
    from anthroforge.core.attachment_provenance import receipt as retained_receipt

    frames = {child.id: frame(document, child)} if child.attachment.parent_instance else None
    return retained_receipt(child, parent, frames)


def invalidate(session: Any, seeds: Any) -> None:
    from . import dependencies, evaluation

    graph = dependencies.graph(session.document)
    outputs = dependencies.closure(dependencies.reverse(graph), seeds)
    targets = {p.owner for p in outputs if p.output == "pose"
               and p.owner in session.document.index.entities}
    if targets:
        evaluation.request(session, targets)
