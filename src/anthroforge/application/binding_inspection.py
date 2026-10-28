"""Current bound-point placement evidence shares existing resolution and surface roles."""

from dataclasses import asdict
from typing import Any

from anthroforge.core.entities import SCP
from anthroforge.core.fibers import Fiber
from anthroforge.core.points import Anchor
from anthroforge.core.surface_references import SurfaceReference

from . import attachment_inspection, placement_inspection, point_evaluation
from .issues import fiber_pins


def bindings(context: Any, target: str) -> list[Any]:
    item = context.document.registry.records.get(target)
    if isinstance(item, Fiber):
        return [
            dict(point=b.point, label=f"Binding {i + 1}", target=b.target, role=b.role)
            for i, b in enumerate(item.bindings)
        ]
    if isinstance(item, Anchor):
        return [dict(point="anchor", label="Anchor", **asdict(item.binding.reference))]
    if isinstance(item, SCP) and item.parent and item.attachment.binding:
        return [dict(point="anchor", label="SCP anchor", target=item.parent, role="SCP_GEOMETRY")]
    return []


def validate(context: Any, target: str, options: Any) -> None:
    if not any(row["point"] == options.get("point") for row in bindings(context, target)):
        raise ValueError("Select an existing anatomical binding to inspect.")


def signature(context: Any, target: str, options: Any) -> Any:
    from .inspection_context import scene_signature

    validate(context, target, options)
    return scene_signature(context.document)


def workload(context: Any, target: str, options: Any) -> Any:
    from anthroforge.core.scheduling import Workload

    return Workload(entities=1, candidates=1)


def resolved(context: Any, target: str, point: str) -> tuple[Any, Any, Any]:
    item = context.document.object(target)
    if isinstance(item, Fiber):
        index = next(i for i, b in enumerate(item.bindings) if b.point == point)
        position = fiber_pins.pin_positions(context, item, [index])[0].tolist()
        return position, item.bindings[index].reference, asdict(item.bindings[index])
    if isinstance(item, Anchor):
        return (
            point_evaluation.position(context.engine, context.document, item),
            item.binding.reference,
            asdict(item.binding),
        )
    return scp_anchor(context, item)


def scp_anchor(context: Any, item: Any) -> tuple[Any, Any, Any]:
    detail = attachment_inspection.describe(context, item)
    if not detail["anchors"]["available"]:
        raise ValueError(detail["anchors"].get("reason", "Binding cannot resolve."))
    ref = SurfaceReference(item.parent, instance=item.attachment.parent_instance)
    return detail["anchors"]["owner_world_metres"], ref, detail


def compute(context: Any, target: str, options: Any, cancel: int) -> dict[str, Any]:
    position, ref, existing = resolved(context, target, options["point"])
    request = dict(position=position, targets=[ref])
    result = placement_inspection.compute(context, target, request, cancel)
    accepted = result["report"].get("confirmed") or {}
    result["report"].update(
        existing_binding=existing,
        binding_point=options["point"],
        support_distance=accepted.get("distance"),
    )
    return result
