"""Per-target bindings, membership and ordering; no destructive Apply/Bake operation."""

from dataclasses import replace
from typing import TYPE_CHECKING, Any

from anthroforge.core.construction import Control, Deformer, Target
from anthroforge.core.entities import SCP
from anthroforge.native import construction as native
from anthroforge.native.scene import entity_frame

from . import construction_codec as codec
from . import construction_tasks as tasks
from . import control_operations as controls
from . import curve_sources, membership
from .control_frames import stable_frame

if TYPE_CHECKING:
    from .session import Session

RELATION_FIELDS = frozenset(
    (
        "id",
        "target",
        "control",
        "kind",
        "bind",
        "members",
        "weighted_members",
        "shrinkwrap",
    )
)


def owner(session: "Session", target: Target) -> Any:
    if target.stage == "LATTICE":
        return controls.editable(session, target.owner)
    return session.editable(target.owner)


def frame(session: "Session", target: Target) -> tuple[float, ...]:
    item = owner(session, target)
    if target.stage == "LATTICE":
        return stable_frame(session, item)
    if target.stage in ("CURVE", "BASE"):
        curve_id = target_curve(item, target)
        definition = curve_sources.resolve(session.engine, session.document, item)
        curve = next(c for c in definition.curves if c.id == curve_id)
        return native.matrix(session.engine, entity_frame(session.engine, item), curve.matrix)
    return entity_frame(session.engine, item)


def target_curve(item: SCP, target: Target) -> str:
    assert item.primitive is not None
    if target.stage == "CURVE":
        return target.component
    return next(p.curve for p in item.primitive.pieces if p.id == target.component)


def install(session: "Session", target: Target, bindings: tuple[Deformer, ...]) -> None:
    item = owner(session, target)
    if target.stage == "LATTICE":
        controls.install(session, replace(item, deformers=bindings))
    else:
        session.replace_entities({item.id: replace(item, deformers=bindings)})
        tasks.edited(session, {item.id})


def add(
    session: "Session",
    control: str,
    target: dict[str, Any],
    indices: list[int] | None = None,
    **options: Any,
) -> str:
    selected, item = Target(**target), session.document.control(control)
    validate_target(session, selected, item.kind)
    binding = new_binding(session, item, selected, indices, options)
    binding = assign_members(session, binding, indices is not None)
    binding = assign_weights(session, binding)
    install(session, selected, (*owner(session, selected).deformers, binding))
    return binding.id


def new_binding(
    session: "Session",
    control: Control,
    target: Target,
    indices: list[int] | None,
    options: dict[str, Any],
) -> Deformer:
    world = stable_frame(session, control)
    bind = native.matrix(session.engine, world, frame(session, target), relative=True)
    settings = dict(codec.tuples(options), indices=tuple(indices or ()), bind=bind)
    return Deformer(control.kind, control.id, target, **settings)


def assign_members(session: "Session", binding: Deformer, restricted: bool) -> Deformer:
    if not restricted:
        return binding
    binding = replace(binding, restrict=True)
    if binding.target.stage == "CURVE":
        owner(session, binding.target)
        curve = curve_sources.source(session.document, binding.target.component)
        return membership.assign(binding, curve)
    return binding


def assign_weights(session: "Session", binding: Deformer) -> Deformer:
    if binding.target.stage != "CURVE":
        return binding
    owner(session, binding.target)
    curve = curve_sources.source(session.document, binding.target.component)
    return membership.assign_weights(binding, curve)


def validate_target(session: "Session", target: Target, kind: str) -> None:
    from anthroforge.core.construction_validation import target as validate

    validate(owner(session, target), target, kind)


def locate(session: "Session", binding: str) -> Deformer:
    items: tuple[SCP | Control, ...] = (*session.document.entities, *session.document.controls)
    for item in items:
        for candidate in item.deformers:
            if candidate.id == binding:
                return candidate
    raise ValueError("Unknown deformer binding: " + binding)


def update(session: "Session", binding: str, **options: Any) -> None:
    current = locate(session, binding)
    if set(options) & RELATION_FIELDS:
        raise ValueError("Use binding operations to change identity, target or bind transform.")
    changed = replace(current, **codec.tuples(options))
    if "indices" in options:
        changed = assign_members(session, changed, True)
    if "weights" in options:
        changed = assign_weights(session, changed)
    bindings = tuple(
        changed if b.id == binding else b for b in owner(session, current.target).deformers
    )
    install(session, current.target, bindings)


def remove(session: "Session", binding: str) -> None:
    current = locate(session, binding)
    install(
        session,
        current.target,
        tuple(b for b in owner(session, current.target).deformers if b.id != binding),
    )


def order(session: "Session", target: dict[str, Any], bindings: list[str]) -> None:
    selected = Target(**target)
    item = owner(session, selected)
    local = {b.id: b for b in item.deformers if b.target == selected}
    if len(bindings) != len(local) or set(bindings) != set(local):
        raise ValueError("Order must contain every binding for this target exactly once.")
    ordered = iter(local[key] for key in bindings)
    install(
        session,
        selected,
        tuple(next(ordered) if b.target == selected else b for b in item.deformers),
    )


def reset(session: "Session", binding: str) -> None:
    current = locate(session, binding)
    if current.kind != "HOOK":
        raise ValueError("Reset binding transforms applies only to Hooks.")
    world = stable_frame(session, session.document.control(current.control))
    bind = native.matrix(session.engine, world, frame(session, current.target), relative=True)
    bindings = tuple(
        replace(b, bind=bind) if b.id == binding else b
        for b in owner(session, current.target).deformers
    )
    install(session, current.target, bindings)


def recenter(session: "Session", binding: str, center: list[float]) -> None:
    update(session, binding, center=center)


def members(session: "Session", binding: str) -> list[int]:
    current = locate(session, binding)
    if current.target.stage == "CURVE":
        item = session.document.entity(current.target.owner)
        assert item.primitive is not None
        curve = curve_sources.source(session.document, current.target.component)
        current = membership.resolve(current, curve)
    return list(current.indices)
