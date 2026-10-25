"""Read-only routing diagnostics use the same resolved Fiber/junction inputs as evaluation."""

from dataclasses import asdict, replace
from typing import Any

from anthroforge.core.construction import Curve
from anthroforge.core.curve_engines import RoutingSettings
from anthroforge.core.routing_obstacles import references
from anthroforge.core.scheduling import Workload
from anthroforge.native import routing_trace

from . import curve_evaluation, curve_sources, routing_evaluation, surface_providers
from .inspection_context import scene_signature


def validate(context: Any, target: str, options: Any) -> None:
    item = context.document.registry.records.get(target)
    if not isinstance(item, Curve) or item.engine != "ROUTED":
        raise ValueError("Select a routed curve or Fiber to inspect its route.")


def backend(context: Any) -> str:
    return (
        context.preferences.value.routing_backend
        if hasattr(context, "preferences")
        else str(context.routing_backend)
    )


def propagation(context: Any) -> str:
    return (context.preferences.value.fiber_propagation if hasattr(context, "preferences")
            else str(context.fiber_propagation))


def signature(context: Any, target: str, options: Any) -> Any:
    validate(context, target, options)
    return scene_signature(context.document), backend(context), propagation(context)


def workload(context: Any, target: str, options: Any) -> Workload:
    item = curve_sources.source(context.document, target)
    settings = item.engine_settings
    return Workload(
        entities=1, candidates=settings.samples if isinstance(settings, RoutingSettings) else 0
    )


def compute(context: Any, target: str, options: Any, cancel: int) -> dict[str, Any]:
    item = curve_sources.source(context.document, target)
    value = curve_evaluation.resolve(
        context.engine, context.document, context.resources, item, cancel, propagation(context)
    )
    inputs = routing_evaluation.capture(
        context.engine, context.document, context.resources, value.authored, value.path
    )
    inputs = replace(
        inputs, backend=backend(context), warm=None if options.get("cold") else inputs.warm
    )
    report = routing_trace.inspect(context.engine, inputs, cancel)
    report.update(provenance(context, target, value.authored, inputs, options))
    return dict(report=report)


def provenance(context: Any, target: str, item: Any, inputs: Any, options: Any) -> dict[str, Any]:
    result = dict(
        target=target, revision=context.document.revision, document=str(context.document.id)
    )
    result.update(
        settings=asdict(item.engine_settings), frame=list(inputs.world), owners=list(inputs.owners)
    )
    result.update(
        surfaces=surfaces(context, item),
        accepted_asset=item.result.asset,
        cold=bool(options.get("cold")),
        coordinates="world metres",
        publication="diagnostic only; accepted path unchanged",
    )
    return result


def surfaces(context: Any, item: Any) -> list[Any]:
    refs = surface_providers.query_references(
        context.engine,
        context.document,
        context.resources.meshes,
        references(context.document, item),
    )
    return [surface_record(context, ref) for ref in refs]


def surface_record(context: Any, reference: Any) -> dict[str, Any]:
    surface = surface_providers.get(
        context.engine, context.document, context.resources.meshes, reference
    )
    return dict(
        target=reference.target,
        role=reference.role,
        name=context.document.object(reference.target).name,
        asset=surface.asset_id,
        result=asdict(surface.result),
        frame=list(surface.frame),
    )


def capture(session: Any, target: str, settings: Any) -> Any:
    from . import tissue_inspection as inspection

    state = inspection.status(session, "route")
    if state["state"] != "ready" or state["target"] != target:
        return None
    report = state["report"]
    index = max(0, min(int(settings.get("index", 0)), len(report["records"]) - 1))
    return dict(index=index, contacts=bool(settings.get("showContacts", True)), report=report)
