"""Persistent alternatives use ordinary editing contexts, not duplicate scene objects."""

from dataclasses import asdict, replace
from typing import Any

from anthroforge.core.reconstruction import SceneSnapshot, Variant

from . import operations, variant_graph
from .editing_contexts import bare


def state(session: Any) -> Any:
    return session.contexts.project(committed=True).reconstruction


def install(session: Any, value: Any) -> None:
    with session.contexts.use(""):
        implicit = session.history.before is None
        if implicit:
            session.begin()
        try:
            session.replace_document(reconstruction=value)
            if implicit:
                session.commit()
        except Exception:
            if implicit and session.history.before is not None:
                session.cancel()
            raise


def create(session: Any, subjects: list[str], name: str = "", enter: bool = True) -> dict[str, Any]:
    require_idle(session)
    document = session.document
    copied, editable, mapping = variant_graph.duplicate(document, session.resources, subjects)
    baseline, current = SceneSnapshot(bare(document)), SceneSnapshot(copied)
    value = state(session)
    name = operations.require_name(name or f"Variant {len(value.variants) + 1}")
    record = variant_record(session, name, subjects, editable, baseline, current, mapping)
    append(session, value, record, (baseline, current))
    if enter:
        select(session, record.id)
    return asdict(record)


def variant_record(
    session: Any, name: str, subjects: Any, editable: Any, baseline: Any, current: Any, mapping: Any
) -> Variant:
    return Variant(
        name,
        tuple(subjects),
        editable,
        baseline.id,
        current.id,
        parent=session._editing.key,
        construction_map=mapping,
    )


def append(session: Any, value: Any, record: Any, snapshots: Any) -> None:
    install(
        session,
        replace(
            value, variants=(*value.variants, record), snapshots=(*value.snapshots, *snapshots)
        ),
    )


def select(session: Any, variant: str = "") -> dict[str, Any]:
    require_idle(session)
    if variant:
        record = state(session).variant(variant)
        if record.checkpoint:
            raise ValueError("Fork a checkpoint before editing it.")
        if variant not in session.contexts.states:
            session.contexts.add(variant, state(session).snapshot(record.current))
    session.contexts.select(variant)
    return inspect(session)


def inspect(session: Any, variant: str = "") -> dict[str, Any]:
    value = state(session)
    return dict(
        active=session.contexts.visible,
        variants=[asdict(v) for v in value.variants],
        selected=asdict(value.variant(variant)) if variant else None,
    )


def checkpoint(session: Any, name: str = "") -> dict[str, Any]:
    require_idle(session)
    active = session._editing.key
    if not active:
        raise ValueError("Choose an editable variant to checkpoint.")
    value, snapshot = state(session), SceneSnapshot(bare(session.document))
    current = value.variant(active)
    record = continued(current, snapshot, name, True)
    append(session, value, record, (snapshot,))
    return asdict(record)


def fork(session: Any, variant: str, name: str = "", enter: bool = True) -> dict[str, Any]:
    require_idle(session)
    value = state(session)
    source = value.variant(variant)
    snapshot, source = fork_snapshot(session, value.snapshot(source.current), source)
    record = continued(source, snapshot, name, False)
    append(session, value, record, (snapshot,))
    if enter:
        select(session, record.id)
    return asdict(record)


def fork_snapshot(session: Any, document: Any, source: Variant) -> tuple[SceneSnapshot, Variant]:
    if document.editing_scope is None:
        document, owned, mapping = variant_graph.duplicate(
            document, session.resources, list(source.subjects)
        )
        source = replace(source, editable=owned, construction_map=mapping)
    return SceneSnapshot(document), source


def continued(source: Any, snapshot: Any, name: str, checkpoint: bool) -> Any:
    suffix = " checkpoint" if checkpoint else " copy"
    return replace(
        source,
        id=snapshot.id,
        current=snapshot.id,
        parent=source.id,
        checkpoint=checkpoint,
        name=operations.require_name(name or source.name + suffix),
    )


def rename(session: Any, variant: str, name: str) -> None:
    value = state(session)
    record = replace(value.variant(variant), name=operations.require_name(name))
    install(
        session,
        replace(value, variants=tuple(record if r.id == variant else r for r in value.variants)),
    )


def require_idle(session: Any) -> None:
    if session.history.before is not None or session.waiting_save:
        raise ValueError("Finish the current gesture or save first.")


def execute(session: Any, operation: str, arguments: Any) -> Any:
    if operation.startswith("variant.review."):
        return review(session, operation.removeprefix("variant.review."), arguments)
    commands = operations_table()
    name = operation.removeprefix("variant.")
    if name not in commands:
        raise ValueError("Unknown variant operation: " + name)
    return commands[name](session, **arguments)


def operations_table() -> dict[str, Any]:
    return {
        "create": create,
        "enter": select,
        "leave": select,
        "inspect": inspect,
        "checkpoint": checkpoint,
        "fork": fork,
        "rename": rename,
    }


def review(session: Any, name: str, arguments: Any) -> Any:
    service = session.variant_review
    commands = {
        "prepare": service.prepare,
        "status": service.status,
        "apply": service.apply,
        "cancel": service.cancel,
    }
    if name not in commands:
        raise ValueError("Unknown variant review operation.")
    return commands[name](**arguments)
