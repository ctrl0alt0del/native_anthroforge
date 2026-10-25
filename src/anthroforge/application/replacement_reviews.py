"""Owned replacement candidates share revision checks and coherent batch publication."""

from dataclasses import asdict, dataclass
from typing import Any

from anthroforge.core.attachment_references import targets
from anthroforge.core.entities import SCP
from anthroforge.core.fibers import Fiber
from anthroforge.core.points import Anchor
from anthroforge.core.replacement_reviews import Change
from anthroforge.core.results import Port
from anthroforge.core.snapshot_definitions import same
from anthroforge.core.tissues import TissueVCP

from . import dependent_tasks, object_revisions, previews
from .resources import Resources


@dataclass(frozen=True)
class Candidate:
    entities: dict[str, Any]
    objects: dict[str, Any]
    resources: Resources
    changes: tuple[Change, ...]
    matching: bool
    baseline: dict[str, Any]
    incoming: frozenset[str]
    members: frozenset[str] = frozenset()
    prepared: frozenset[Port] = frozenset()


def bundle(
    document: Any,
    target: str,
    entities: Any,
    objects: Any,
    before: Any,
    resources: Any,
    changes: Any,
    matching: bool,
) -> Candidate:
    resources = additions(before, resources)
    return with_baseline(document, target, entities, objects, resources, changes, matching)


def with_baseline(
    document: Any,
    target: str,
    entities: Any,
    objects: Any,
    resources: Any,
    changes: Any,
    matching: bool,
) -> Candidate:
    baseline = {key: document.object(key) for key in entities.keys() | objects.keys()}
    references = frozenset(item.id for item in incoming(document, target))
    members = frozenset(document.registry.records)
    return Candidate(entities, objects, resources, changes, matching, baseline, references, members)


def additions(before: Resources, after: Resources) -> Resources:
    return Resources(
        **{
            name: {
                key: value
                for key, value in getattr(after, name).items()
                if key not in getattr(before, name)
            }
            for name in Resources.__dataclass_fields__
        }
    )


def install_records(session: Any, candidate: Candidate) -> None:
    entities = session.authored_entities(candidate.entities)
    objects = {
        key: object_revisions.authored(session.document.object(key), item)
        for key, item in candidate.objects.items()
    }
    ports = changed_object_ports(session, objects)
    session.scheduler.invalidate_ports(ports)
    session.replace_document(
        entities=replaced(session.document.entities, entities),
        objects=replaced(session.document.objects, objects),
    )
    publish_changes(session, candidate, ports)


def replaced(records: Any, changes: Any) -> tuple[Any, ...]:
    return tuple(changes.get(item.id, item) for item in records)


def require_unchanged(session: Any, target: str, candidate: Candidate) -> None:
    require_members(session, candidate)
    records = session.document.registry.records
    if any(
        key not in records or not same(before, records[key])
        for key, before in candidate.baseline.items()
    ):
        raise ValueError("Replacement definitions changed; assess again.")
    references = frozenset(item.id for item in incoming(session.document, target))
    if references != candidate.incoming:
        raise ValueError("Incoming relationships changed; assess again.")


def changed_object_ports(session: Any, objects: dict[str, Any]) -> set[Port]:
    return set().union(
        *(
            object_revisions.changed_ports(session.document.object(key), item)
            for key, item in objects.items()
        )
    )


def current(session: Any, value: Any) -> bool:
    if not previews.current(session, value):
        return False
    try:
        if value.asset:
            require_unchanged(session, value.target, value.asset)
        return True
    except ValueError:
        return False


def change_rows(session: Any, candidate: Candidate) -> list[dict[str, Any]]:
    return [
        dict(asdict(row), name=candidate.baseline[row.target].name) for row in candidate.changes
    ]


def incoming(document: Any, target: str) -> tuple[Any, ...]:
    return tuple(
        item
        for item in document.registry.records.values()
        if (isinstance(item, SCP) and item.parent == target) or target in targets(item)
    )


def publish_changes(session: Any, candidate: Candidate, ports: set[Port]) -> None:
    if candidate.prepared:
        from .ready_bundles import changed

        changed(session, set(candidate.prepared), ports)
    else:
        dependent_tasks.changed(session, ports, published=False)


def description(item: Any) -> str:
    if isinstance(item, Fiber):
        return "Recapture this Fiber's deformation supports and pins from its accepted shape."
    if isinstance(item, Anchor):
        return "Recapture this Anchor on the same target from its accepted position."
    if isinstance(item, TissueVCP):
        return "Recapture target-relative tissue region goals on the same target."
    return "Recapture this child SCP's attachment while preserving its current pose."


def requires_rebind(item: Any) -> bool:
    return not isinstance(item, SCP) or item.attachment.parent_mode == "SURFACE_NEAREST"


def binding_changes(document: Any, target: str) -> list[Change]:
    return [
        Change("rebind:" + item.id, item.id, "REBIND", description(item))
        for item in incoming(document, target)
        if requires_rebind(item)
    ]


def require_members(session: Any, candidate: Candidate) -> None:
    if frozenset(session.document.registry.records) != candidate.members:
        raise ValueError("Document membership changed; assess replacement again.")
