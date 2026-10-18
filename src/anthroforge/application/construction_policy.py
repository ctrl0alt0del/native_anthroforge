"""Shared authoring constraints used by desktop and headless operations."""

from anthroforge.core.document import Document
from anthroforge.core.results import Port, ReadRevision


def topology_dependents(document: Document, entity: str) -> tuple[str, ...]:
    children = [e.id for e in document.entities if e.parent == entity]
    controls = [
        c.id
        for c in document.controls
        if c.support == entity and c.attachment.parent_mode == "SURFACE_NEAREST"
    ]
    return tuple((*children, *controls))


def topology_locks(document: Document, target: str) -> list[dict[str, str]]:
    from .curve_sources import consumers

    owners = consumers(document, {target}) if target in document.registry.construction else {target}
    return [
        dict(
            id=key,
            name=document.object(key).name,
            consumer=owner,
            reason="Incoming attachment on " + document.object(owner).name,
        )
        for owner in sorted(owners)
        for key in topology_dependents(document, owner)
    ]


def require_topology_edit(document: Document, entity: str) -> None:
    dependents = topology_dependents(document, entity)
    if dependents:
        raise ValueError(
            "Topology is locked by children or surface attachments: " + ", ".join(dependents)
        )


def mode(document: Document, entity: str) -> str:
    from anthroforge.core.construction import Control

    item = document.object(entity)
    setting = "INHERIT" if isinstance(item, Control) else item.update_mode
    return document.update_mode if setting == "INHERIT" else setting


def revisions(document: Document, ports: set[Port]) -> tuple[ReadRevision, ...]:
    return tuple(
        revision(document, port) for port in sorted(ports, key=lambda p: (p.owner, p.output))
    )


def revision(document: Document, port: Port) -> ReadRevision:
    if port.owner in document.registry.construction:
        return object_revision(document, port)
    if port.output in ("control", "cage"):
        control = document.control(port.owner)
        return ReadRevision(port.owner, port.output, control.generation, 0)
    entity = document.entity(port.owner)
    if port.output == "pose":
        return ReadRevision(port.owner, port.output, 0, entity.pose_revision)
    return ReadRevision(
        port.owner, port.output, entity.construction_revision, entity.result.revision
    )


def object_revision(document: Document, port: Port) -> ReadRevision:
    item = document.registry.construction[port.owner]
    pose = port.output in ("pose", "local_pose")
    authored = item.pose_revision if pose else item.construction_revision
    accepted = 0 if pose else item.result.revision
    return ReadRevision(port.owner, port.output, authored, accepted)
