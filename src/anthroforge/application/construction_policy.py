"""Shared authoring constraints used by desktop and headless operations."""

from anthroforge.core import attachment_references
from anthroforge.core.document import Document
from anthroforge.core.results import Port, ReadRevision
from anthroforge.core.tissue_revisions import PHASES
from anthroforge.core.tissues import TissueVCP


def topology_dependents(document: Document, entity: str) -> tuple[str, ...]:
    children = [e.id for e in document.entities if e.parent == entity]
    return tuple((*children, *bound_fibers(document, entity)))


def bound_fibers(document: Document, entity: str) -> tuple[str, ...]:
    return tuple(
        item.id for item in document.objects if entity in attachment_references.targets(item)
    )


def topology_locks(document: Document, target: str) -> list[dict[str, str]]:
    owners = downstream(document, target)
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
    dependents = sorted({row["id"] for row in topology_locks(document, entity)})
    if dependents:
        raise ValueError(
            "Topology is locked by children or surface attachments: " + ", ".join(dependents)
        )


def downstream(document: Document, target: str) -> set[str]:
    from .dependencies import closure

    return closure(document.registry.consumers, {target})


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
    if port.owner in document.registry.authored:
        return object_revision(document, port)
    if port.owner in document.index.controls:
        control = document.control(port.owner)
        return ReadRevision(port.owner, port.output, control.generation, 0)
    entity = document.entity(port.owner)
    if port.output == "pose":
        return ReadRevision(port.owner, port.output, 0, entity.pose_revision)
    return ReadRevision(
        port.owner, port.output, entity.construction_revision, entity.result.revision
    )


def object_revision(document: Document, port: Port) -> ReadRevision:
    if port.output == "stack_scope":
        from .tissue_stack_observation import membership

        return ReadRevision(port.owner, port.output, 0, 0, membership(document))
    if port.output == "routing_scope":
        scope = document.index.structure.dependencies.routing_scene
        return ReadRevision(port.owner, port.output, 0, 0, scope)
    item = document.registry.authored[port.owner]
    if isinstance(item, TissueVCP) and port.output in PHASES:
        return tissue_revision(item, port)
    pose = port.output in ("pose", "local_pose")
    authored = item.pose_revision if pose else item.construction_revision
    accepted = 0 if pose else item.result.revision
    return ReadRevision(port.owner, port.output, authored, accepted)


def tissue_revision(item: TissueVCP, port: Port) -> ReadRevision:
    result = getattr(item, port.output + "_result")
    return ReadRevision(
        item.id, port.output, getattr(item, port.output + "_revision"), result.revision
    )
