"""A read-only worker evaluates a complete retargeted tissue using existing native phases."""

from dataclasses import dataclass, field, replace
from typing import Any
from uuid import uuid4

from anthroforge.core.results import Port
from anthroforge.core.tissues import TissueVCP
from anthroforge.native import topology

from . import (
    dependencies,
    object_revisions,
    tissue_evaluation,
    tissue_fields,
    tissue_region_goals,
    tissue_results,
)
from . import tissue_retarget_policy as policy
from .assets import Asset


@dataclass
class Assessment:
    engine: Any
    original: Any
    document: Any
    resources: Any
    item: TissueVCP
    edits: policy.Edits
    cancel: int
    related: dict[str, Any] = field(default_factory=dict)
    base_matching: bool = False

    def install(self, item: Any) -> None:
        original = self.original.object(item.id)
        self.item = object_revisions.authored(original, item)
        self.document = replace(
            self.document,
            objects=tuple(self.item if o.id == item.id else o for o in self.document.objects),
        )

    def phase(self, name: str) -> None:
        self.install(self.item)
        port = Port(self.item.id, name)
        if port in dependencies.blocked(dependencies.graph(self.document)):
            raise ValueError("The selected source creates a cyclic or missing tissue dependency.")
        output = tissue_evaluation.evaluate(
            self.engine, self.document, self.resources, self.item.id, name, self.cancel
        )
        key = registered(self.resources, name, output)
        ports = dependencies.ports(self.document, port)
        result = tissue_results.accept(self.document, self.item, name, ports, key, output)
        self.install(
            replace(self.item, **tissue_results.publication(self.item, name, result, output))
        )

    def evaluate(self) -> None:
        self.phase("base")
        reconcile_parts(self)
        self.base_matching = matching_base(self)
        reconcile_fields(self, "BASE")
        reconcile_crop(self)
        self.phase("rest")
        reconcile_fields(self, "REST")
        reconcile_regions(self)
        reconcile_stacking(self)
        for phase in ("intrinsic", "plan", "final"):
            self.phase(phase)


def registered(resources: Any, phase: str, output: Any) -> str:
    if output.mesh is None:
        return str(output.asset)
    key = str(uuid4())
    resources.meshes[key] = Asset(output.mesh, "replacement tissue " + phase, "", 1.0, False)
    return key


def matching_base(context: Assessment) -> bool:
    before, after = context.original.object(context.item.id), context.item
    if (
        before.base_state.kind != after.base_state.kind
        or before.base_state.parts != after.base_state.parts
    ):
        return False
    try:
        return tissue_fields.domain(context.resources, before, "BASE") == tissue_fields.domain(
            context.resources, after, "BASE"
        )
    except (KeyError, ValueError):
        return False


def reconcile_fields(context: Assessment, name: str) -> None:
    count, signature = tissue_fields.domain(context.resources, context.item, name)
    invalid = {
        f.name
        for f in context.item.fields
        if f.domain == name and (len(f.values) != count or f.topology != signature)
    }
    for key in sorted(invalid):
        context.edits.note(
            "field:" + key, "Discard field " + key + "; its material domain changed."
        )
    item = replace(
        context.item, fields=tuple(f for f in context.item.fields if f.name not in invalid)
    )
    context.install(policy.compatible_regions(item, context.edits))


def reconcile_crop(context: Assessment) -> None:
    if context.item.crop.enabled and not context.base_matching:
        context.edits.note(
            "crop_material", "Initialize the existing crop plane on the new material domain."
        )
        context.install(replace(context.item, intrinsic_material=None))


def reconcile_regions(context: Assessment) -> None:
    _, signature = tissue_fields.domain(context.resources, context.item, "REST")
    rows = []
    for row in context.item.constraints:
        if row.reference is not None and row.topology != signature:
            row = recapture_region(context, row)
        rows.append(row)
    context.install(replace(context.item, constraints=tuple(rows)))


def recapture_region(context: Assessment, row: Any) -> Any:
    batch, material, signature = tissue_region_goals.capture(
        context.engine,
        context.document,
        context.resources,
        context.item,
        row.reference,
        context.cancel,
    )
    key = str(uuid4())
    context.resources.bindings[key] = batch
    context.edits.note(
        "region_capture:" + row.id, "Recapture target-relative region " + row.mask + "."
    )
    return replace(row, binding_asset=key, material_asset=material, topology=signature)


def reconcile_stacking(context: Assessment) -> None:
    changed = stack_changes(context)
    context.related.update(changed)
    context.document = replace(
        context.document, objects=tuple(changed.get(o.id, o) for o in context.document.objects)
    )
    context.item = context.document.object(context.item.id)


def stack_changes(context: Assessment) -> dict[str, Any]:
    changed = {}
    for item in context.document.objects:
        if not isinstance(item, TissueVCP):
            continue
        rows = tuple(
            updated
            for row in item.stack_relationships
            if (updated := relationship(context, item, row)) is not None
        )
        if rows != item.stack_relationships:
            changed[item.id] = object_revisions.authored(
                item, replace(item, stack_relationships=rows)
            )
    return changed


def relationship(context: Assessment, item: Any, row: Any) -> Any:
    own, other = item.id == context.item.id, row.other == context.item.id
    if not own and not other:
        return row
    side = row.side if own else row.other_side
    if context.item.base_state.kind != "SURFACE" or (side == "b" and not context.item.both_sides):
        return discarded_relationship(context, item, row)
    covers_target = own and row.cover == "SELF" or other and row.cover == "OTHER"
    if row.regions and covers_target and not context.base_matching:
        return cleared_regions(context, item, row)
    return row


def matching_final(context: Assessment) -> bool:
    before, after = context.original.object(context.item.id), context.item
    if not context.base_matching or not before.final_result.asset:
        return False
    meshes = context.resources.meshes
    return topology.same_topology(
        meshes[before.final_result.asset].mesh,
        meshes[after.final_result.asset].mesh,
        context.cancel,
    )


def discarded_relationship(context: Assessment, item: Any, row: Any) -> None:
    key = relationship_key("stack_drop", item, row)
    context.edits.note(
        key, "Remove incompatible stacking relationship with " + row.other + ".", item.id
    )
    return None


def cleared_regions(context: Assessment, item: Any, row: Any) -> Any:
    key = relationship_key("stack_regions", item, row)
    context.edits.note(key, "Clear selected support regions on the changed domain.", item.id)
    return replace(row, regions=(), topology="")


def relationship_key(action: str, item: Any, row: Any) -> str:
    return ":".join((action, item.id, row.other, row.side, row.other_side))


def reconcile_parts(context: Assessment) -> None:
    existing = {part.id for part in context.item.parts}
    missing = set(context.item.base_state.parts) - existing
    if missing:
        context.edits.note(
            "parts",
            "Use main settings for "
            + str(len(missing))
            + " new construction parts; retain inactive part settings.",
        )
