"""Shared-control authoring. Bindings are independent of the control's lifetime."""

from dataclasses import replace
from typing import TYPE_CHECKING, Any

from anthroforge.core.construction import Control, Deformer, Target
from anthroforge.core.entities import IDENTITY, SCP, Attachment
from anthroforge.core.results import geometry_asset
from anthroforge.native import construction as native
from anthroforge.native.mesh import NativeCancellation

from . import construction_codec as codec
from . import construction_tasks as tasks
from . import dependencies as dep
from .construction_evaluator import Evaluation
from .control_frames import detached, remember, stable_frame
from .presentation import include_created

if TYPE_CHECKING:
    from .session import Session


def evaluation(session: "Session") -> Evaluation:
    return Evaluation(
        session.engine,
        session.document,
        {k: a.mesh for k, a in session.assets.items()},
        NativeCancellation(session.engine),
    )


def editable(session: "Session", control: str) -> Control:
    if session.waiting_save:
        raise ValueError("Editing is blocked while waiting to save.")
    if session.workspace.focused and control not in session.workspace.members:
        raise ValueError("This control is outside the focused workspace and is read-only.")
    return session.document.control(control)


def install(session: "Session", item: Control) -> None:
    from .control_tasks import edited

    item = replace(item, generation=item.generation + 1)
    controls = tuple(item if c.id == item.id else c for c in session.document.controls)
    session.scheduler.invalidate({item.id})
    session.replace_document(controls=controls)
    edited(session, {dep.Port(item.id, "control")})
    targets = dep.affected(
        session.document, {dep.Port(item.id, "control"), dep.Port(item.id, "cage")}
    )
    tasks.edited(session, targets)


def add(session: "Session", item: Control) -> str:
    item = remember(item, evaluation(session).follow_frame(item))
    session.replace_document(controls=(*session.document.controls, item))
    include_created(session, {item.id})
    return item.id


def create(
    session: "Session",
    kind: str = "HOOK",
    entity: str = "",
    name: str = "Control",
    values: list[float] | None = None,
) -> str:
    validate_owner(session, entity)
    transform = session.engine.transform(values) if values else IDENTITY
    points = new_cage_points(session, kind)
    if kind == "LATTICE" and entity and values is None:
        transform = fitted_cage(session, entity)
    item = Control(name, kind, follow=entity, matrix=transform, points=points)
    return add(session, item)


def new_cage_points(session: "Session", kind: str) -> tuple[tuple[float, ...], ...]:
    points = native.lattice_grid(session.engine, (2, 2, 2)) if kind == "LATTICE" else ()
    return tuple(tuple(p) for p in points)


def validate_owner(session: "Session", entity: str) -> None:
    if entity:
        session.editable(entity)


def fitted_cage(session: "Session", entity: str) -> tuple[float, ...]:
    item = session.document.entity(entity)
    key = geometry_asset(item)
    if not key:
        raise ValueError("Evaluate the primitive before fitting its lattice.")
    b = session.assets[key].mesh.bounds
    center = [(b[i] + b[i + 3]) * 0.5 + item.geometry_offset[i] for i in range(3)]
    size = [max(b[i + 3] - b[i], 0.01) for i in range(3)]
    return session.engine.transform([*center, 0, 0, 0, *size])


def transform(session: "Session", control: str, values: list[float]) -> None:
    item = editable(session, control)
    changed = replace(item, matrix=session.engine.transform(values))
    if item.support and any(e.id == item.support for e in session.document.entities):
        surface = item.attachment.parent_mode == "SURFACE_NEAREST"
        changed = surface_attached(session, changed, item.support, changed.matrix, surface)
    install(session, changed)


def follow(session: "Session", control: str, entity: str = "") -> None:
    item = editable(session, control)
    world = stable_frame(session, item)
    parent = session.document.entity(entity).matrix if entity else IDENTITY
    local = native.matrix(session.engine, parent, world, relative=True)
    install(
        session, replace(item, follow=entity, matrix=local, support="", attachment=Attachment())
    )


def update(session: "Session", control: str, **options: Any) -> None:
    item = editable(session, control)
    if set(options) - {"name", "interpolation", "outside", "weights"}:
        raise ValueError("Unknown control setting.")
    install(session, replace(item, **codec.tuples(options)))


def lattice_point(session: "Session", control: str, index: int, position: list[float]) -> None:
    item = editable(session, control)
    if item.kind != "LATTICE" or not 0 <= index < len(item.points):
        raise ValueError("Unknown lattice point.")
    points = list(item.points)
    points[index] = tuple(position)
    install(session, replace(item, points=tuple(points)))


def lattice_resize(session: "Session", control: str, resolution: list[int]) -> None:
    item = editable(session, control)
    dimensions = native.lattice_resolution(session.engine, resolution)
    points = native.lattice_grid(session.engine, dimensions)
    linear = replace(item, interpolation=("LINEAR",) * 3, weights=())
    binding = Deformer("LATTICE", control, Target(control, "LATTICE"))
    resized = native.lattice(session.engine, points, linear, binding, IDENTITY, IDENTITY, 0)
    install(session, resized_cage(item, resized, dimensions))


def resized_cage(item: Control, points: Any, dimensions: tuple[int, ...]) -> Control:
    bindings = tuple(replace(b, weights=(), weighted_members=()) for b in item.deformers)
    return replace(
        item,
        points=tuple(tuple(p) for p in points),
        resolution=dimensions,
        weights=(),
        deformers=bindings,
    )


def affected(session: "Session", control: str) -> list[str]:
    return sorted(
        dep.affected(session.document, {dep.Port(control, "control"), dep.Port(control, "cage")})
    )


def delete(session: "Session", control: str) -> dict[str, Any]:
    editable(session, control)
    targets = affected(session, control)
    entities = tuple(
        without_bindings(e, control, e.id in targets) for e in session.document.entities
    )
    controls = tuple(
        detach_reference(session, c, control) for c in session.document.controls if c.id != control
    )
    changed = {c.id for c in controls if c != session.document.control(c.id)}
    session.scheduler.invalidate({control, *targets})
    session.replace_document(entities=entities, controls=controls)
    refresh_references(session, changed)
    tasks.edited(session, set(targets))
    return {"deleted": control, "affected": targets}


def refresh_references(session: "Session", controls: set[str]) -> None:
    from .control_tasks import edited

    seeds = {dep.Port(key, "control") for key in controls}
    edited(session, seeds)
    tasks.edited(session, dep.affected(session.document, seeds))


def without_bindings(item: SCP, control: str, affected: bool) -> SCP:
    return replace(
        item,
        deformers=tuple(b for b in item.deformers if b.control != control),
        generation=item.generation + int(affected),
    )


def detach_reference(session: "Session", item: Control, removed: str) -> Control:
    deformers = tuple(b for b in item.deformers if b.control != removed)
    if item.support != removed:
        return replace(
            item, deformers=deformers, generation=item.generation + int(deformers != item.deformers)
        )
    return replace(detached(session, item), deformers=deformers)


def attach(session: "Session", control: str, support: str, surface: bool = True) -> None:
    item = editable(session, control)
    world = stable_frame(session, item)
    item = remember(item, world)
    other = next((c for c in session.document.controls if c.id == support), None)
    if other:
        parent = stable_frame(session, other)
        local = native.matrix(session.engine, parent, world, relative=True)
        install(session, replace(item, support=support, follow="", matrix=local))
    else:
        install(session, surface_attached(session, item, support, world, surface))


def surface_attached(
    session: "Session", item: Control, support: str, world: tuple[float, ...], surface: bool
) -> Control:
    session.document.entity(support)
    settings = Attachment(
        parent_mode="SURFACE_NEAREST" if surface else "OBJECT_ORIGIN", child_mode="OBJECT_ORIGIN"
    )
    result = replace(item.result, matrix=world, binding=())
    return replace(
        item, support=support, follow="", matrix=world, attachment=settings, result=result
    )
