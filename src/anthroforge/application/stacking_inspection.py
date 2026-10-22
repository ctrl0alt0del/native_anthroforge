"""Read-only support evidence for an accepted order, separate from authored overrides."""

from contextlib import contextmanager
from dataclasses import asdict
from typing import Any

from anthroforge.core.results import geometry_asset
from anthroforge.core.scheduling import Workload
from anthroforge.native import stack_inspection
from anthroforge.native.stacking import dependencies

from . import tissue_stack_evaluation as evaluation
from . import tissue_stack_scene as scene
from .object_frames import Frames
from .tissue_inspection_stages import tissue


def validate(context: Any, target: str, options: Any) -> None:
    item, other = tissue(context, target), tissue(context, options.get("other", ""))
    if item.id == other.id or not item.stacking:
        raise ValueError("Choose two different participants of enabled tissue stacking.")
    if any(o.base_state.kind != "SURFACE" for o in (item, other)):
        raise ValueError("Stacking footprints require two surface tissues.")


def accepted(item: Any) -> None:
    if item.plan_result.status != "ready" or item.plan_result.error or item.stack_plan.error:
        raise ValueError("Stacking order is not current. Evaluate it before inspecting footprints.")


def signature(context: Any, target: str, options: Any) -> Any:
    validate(context, target, options)
    frames = Frames(context.engine, context.document)
    participants = tuple(
        (participant(o), frames.world(o.id)) for o in scene.participants(context.document)
    )
    obstacles = tuple(
        (o.id, geometry_asset(o), o.matrix, o.geometry_offset) for o in context.document.entities
    )
    return str(context.document.id), target, options, participants, obstacles


def participant(item: Any) -> Any:
    return (
        item.id,
        item.intrinsic_material,
        item.intrinsic_result,
        item.stack_plan,
        item.plan_result,
        item.stack_settings,
        item.stack_relationships,
        item.group,
    )


def workload(context: Any, target: str, options: Any) -> Workload:
    triangles = sum(
        context.assets[o.intrinsic_result.asset].mesh.counts[3]
        for o in scene.participants(context.document)
    )
    return Workload(triangles=triangles)


def compute(context: Any, target: str, options: Any, cancel: int) -> dict[str, Any]:
    item = tissue(context, target)
    with prepare(context, item, cancel) as (captured, native):
        order = selected_order(item, options)
        report = describe(context, item, order)
        report["active"] = active(native, order)
        report.update(footprint(captured, native, order, cancel))
        return dict(report=report, lines=report["lines"])


def active(native: Any, order: Any) -> bool:
    if not order.covering or not order.underlying:
        return False
    sides = {order.first: order.side, order.second: order.other_side}
    pair = (
        scene.identity(order.covering, sides[order.covering]),
        scene.identity(order.underlying, sides[order.underlying]),
    )
    return pair in dependencies(native)


@contextmanager
def prepare(context: Any, item: Any, cancel: int) -> Any:
    accepted(item)
    with evaluation.prepared(
        context.engine, context.document, context.resources, item, cancel
    ) as values:
        verify_plan(item, *values)
        yield values[:2]


def verify_plan(item: Any, captured: Any, native: Any, output: Any, orders: Any) -> None:
    providers = {
        captured.identities[b][0]
        for a, b in dependencies(native)
        if captured.identities[a][0] == item.id
    }
    if evaluation.description(captured, providers, output, orders) != item.stack_plan:
        raise ValueError("The accepted stacking plan differs from current inputs. Reevaluate it.")


def selected_order(item: Any, options: Any) -> Any:
    pair = {(item.id, options.get("side", "a")), (options["other"], options.get("other_side", "a"))}
    order = next(
        (
            r
            for r in item.stack_plan.orders
            if {(r.first, r.side), (r.second, r.other_side)} == pair
        ),
        None,
    )
    if order is None:
        raise ValueError("No accepted order exists for these tissue sides.")
    return order


def describe(context: Any, item: Any, order: Any) -> dict[str, Any]:
    names = {key: context.document.object(key).name for key in (order.first, order.second)}
    assets = {key: context.document.object(key).intrinsic_result.asset for key in names}
    return dict(
        order=asdict(order),
        names=names,
        assets=assets,
        frames={key: context.document.object(key).intrinsic_material.frame for key in names},
        revision=context.document.revision,
        plan_revision=item.plan_result.revision,
        method="Production material support masks on accepted intrinsic surfaces",
    )


def footprint(captured: Any, native: Any, order: Any, cancel: int) -> dict[str, Any]:
    if order.status != 0 or not order.underlying or not order.covering:
        return dict(lines=[], polygons=0, truncated=False, surface="No supported relationship")
    sides = {order.first: order.side, order.second: order.other_side}
    cover = scene.identity(order.covering, sides[order.covering])
    provider = scene.identity(order.underlying, sides[order.underlying])
    if cover not in captured.identities or provider not in captured.identities:
        raise ValueError("Accepted stacking participants are unavailable.")
    return stack_inspection.footprint(native, cover, provider, cancel)
