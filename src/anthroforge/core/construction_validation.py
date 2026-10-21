"""Construction reference integrity; general dependency cycles remain authorable."""

from typing import TYPE_CHECKING

from .construction import Control, Deformer, Primitive, Target, Thickness
from .construction_capabilities import stable_geometry_members
from .entities import SCP

if TYPE_CHECKING:
    from .document import Document


def target(item: SCP | Control, reference: Target, kind: str) -> None:
    if reference.owner != item.id:
        raise ValueError("Binding must belong to its target owner.")
    if kind in ("SUBDIVISION", "DISPLACE") and reference.stage != "GEOMETRY":
        raise ValueError("This modifier requires generated geometry.")
    if isinstance(item, Control):
        if item.kind != "LATTICE" or kind != "HOOK" or reference.stage != "LATTICE":
            raise ValueError("Lattice points support Hook bindings.")
    elif item.primitive is None:
        raise ValueError("A grouping SCP has no deformation target.")
    else:
        primitive_target(item, reference)
    if reference.stage in ("GEOMETRY", "LATTICE") and reference.component:
        raise ValueError("This target stage has no component identifier.")


def primitive_target(item: SCP, reference: Target) -> None:
    assert item.primitive is not None
    stages = {
        "GEOMETRY": {""},
        "CURVE": {c.id for c in item.primitive.curves},
        "BASE": {p.id for p in item.primitive.pieces},
    }
    if reference.component not in stages.get(reference.stage, set()):
        raise ValueError("Unknown primitive target stage or owned component.")


def identities(item: SCP | Control) -> list[str]:
    result = [item.id, *(binding.id for binding in item.deformers)]
    if isinstance(item, SCP) and item.primitive:
        if not isinstance(item.primitive, Primitive):
            raise ValueError(
                "Document stores primitive references, not resolved evaluation inputs."
            )
        result.extend(p.id for p in item.primitive.pieces)
    return result


def binding(item: SCP | Control, value: Deformer, controls: dict[str, Control]) -> None:
    if value.kind in ("HOOK", "LATTICE") and (
        value.control not in controls or controls[value.control].kind != value.kind
    ):
        raise ValueError("Binding requires a shared control of the matching kind.")
    target(item, value.target, value.kind)
    if value.target.stage == "GEOMETRY" and not stable_geometry_members(item):
        if value.indices or value.members or value.weights or value.weighted_members:
            raise ValueError(
                "Segment Chain has changing geometry membership; use whole-target "
                "deformation or assign weights to a lattice cage instead."
            )


def control_references(control: Control, parents: set[str], anatomy: set[str]) -> None:
    if control.follow and control.follow not in parents:
        raise ValueError("Control transform source does not exist.")
    if set(control.owners) - anatomy:
        raise ValueError("Control workspace associations require anatomical objects.")


def transform_parents(document: "Document") -> set[str]:
    from .reference_images import ReferenceImage

    return {
        o.id
        for o in (*document.entities, *document.controls, *document.objects)
        if not isinstance(o, ReferenceImage)
    }


def thickness_membership(item: SCP, thickness: Thickness | None) -> None:
    if not stable_geometry_members(item) and thickness and thickness.weights:
        raise ValueError("Segment Chain has changing vertex membership; use uniform thickness.")


def item_membership(item: SCP | Control, controls: dict[str, Control]) -> None:
    if isinstance(item, SCP):
        thickness_membership(item, item.thickness)
    for value in item.deformers:
        binding(item, value, controls)


def document(document: "Document") -> None:
    items: tuple[SCP | Control, ...] = (*document.entities, *document.controls)
    keys = [key for item in items for key in identities(item)]
    if any(not key for key in keys) or len(keys) != len(set(keys)):
        raise ValueError("Authored identities must be nonempty and unique across the document.")
    controls = {c.id: c for c in document.controls}
    parents, anatomy = transform_parents(document), {e.id for e in document.entities}
    for control in document.controls:
        control_references(control, parents, anatomy)
    for item in items:
        item_membership(item, controls)
