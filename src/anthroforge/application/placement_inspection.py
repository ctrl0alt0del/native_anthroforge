"""Explain a current placement query without recapturing or changing any binding."""

from dataclasses import asdict
from typing import Any

from anthroforge.core.scheduling import Workload
from anthroforge.native import inspection, inspection_placement, measurement

from . import surface_providers, surface_queries
from .construction_policy import revisions
from .placement_inputs import ray


def references(context: Any, options: Any) -> tuple[Any, ...]:
    return tuple(surface_providers.normalize(context.document, ref) for ref in options["targets"])


def validate(context: Any, target: str, options: Any) -> None:
    refs = references(context, options)
    if not 1 <= len(refs) <= 4096:
        raise ValueError("Choose 1–4096 accepted anatomical surfaces.")
    ray(refs, options["position"], options.get("direction") or (0, 0, 1), options.get("offset", 0))
    for ref in refs:
        surface_providers.get(context.engine, context.document, context.assets, ref)


def signature(context: Any, target: str, options: Any) -> Any:
    validate(context, target, options)
    refs = references(context, options)
    return str(context.document.id), revisions(
        context.document, surface_providers.ports(context.document, refs)
    )


def workload(context: Any, target: str, options: Any) -> Workload:
    refs = references(context, options)
    return Workload(
        triangles=sum(
            surface_providers.triangle_count(context.document, context.assets, r) for r in refs
        )
    )


def compute(context: Any, target: str, options: Any, cancel: int) -> dict[str, Any]:
    refs = references(context, options)
    providers = [
        surface_providers.get(context.engine, context.document, context.assets, r) for r in refs
    ]
    preview = evaluate(context, providers, options, surface_queries.Mode.PREVIEW, cancel)
    try:
        confirmed = evaluate(context, providers, options, surface_queries.Mode.CONFIRMED, cancel)
        error = ""
    except ValueError as failure:
        confirmed, error = None, str(failure)
    return dict(report=report(context, target, options, providers, preview, confirmed, error))


def evaluate(context: Any, providers: Any, options: Any, mode: Any, cancel: int) -> Any:
    queries = [
        surface_queries.prepare(context.document, context.assets, p, mode, cancel)
        for p in providers
    ]
    handles, frames = [q.mesh.handle for q in queries], [p.frame for p in providers]
    request = [
        *options["position"],
        *(options.get("direction") or (0, 0, 0)),
        options.get("offset", 0),
    ]
    result = inspection_placement.inspect(
        context.engine, handles, frames, request, bool(options.get("direction")), cancel
    )
    return candidate_report(context, providers, result)


def candidate_report(context: Any, providers: Any, result: Any) -> Any:
    if result["winner"] < 0:
        return dict(hit=False, candidates=result["candidates"], lines=[])
    index = result["winner"]
    provider, row = providers[index], result["candidates"][index]
    lines = inspection.face_lines(provider.resource.mesh, provider.frame, row["triangle"])
    return dict(
        row,
        **provider_record(context, provider),
        lines=lines,
        candidates=result["candidates"],
        winner=index,
    )


def provider_record(context: Any, provider: Any) -> dict[str, Any]:
    return dict(
        reference=asdict(provider.reference),
        asset=provider.asset_id,
        frame=provider.frame,
        revision=provider.result.revision,
        name=context.document.object(provider.reference.target).name,
    )


def report(
    context: Any,
    target: str,
    options: Any,
    providers: Any,
    preview: Any,
    confirmed: Any,
    error: str,
) -> Any:
    accepted = confirmed if confirmed and confirmed["hit"] else None
    result = base_report(context, target, options, providers)
    result.update(preview=preview, confirmed=confirmed, error=error)
    result.update(displacement=displacement(context, preview, accepted))
    return dict(result, lines=lines(options, preview, accepted))


def displacement(context: Any, preview: Any, accepted: Any) -> Any:
    return (
        measurement.distance(context.engine, preview["accepted"], accepted["accepted"])
        if preview["hit"] and accepted
        else None
    )


def base_report(context: Any, target: str, options: Any, providers: Any) -> dict[str, Any]:
    return dict(
        target=target,
        revision=context.document.revision,
        requested=options["position"],
        direction=options.get("direction"),
        targets=[asdict(p.reference) for p in providers],
        method="ray" if options.get("direction") else "nearest",
        explanation=(
            "Current preview versus exterior-qualified placement; not a historical gesture. "
            "Stored bindings remain unchanged."
        ),
        local_exit="Unavailable: no volume-exit classification is performed.",
    )


def lines(options: Any, preview: Any, confirmed: Any) -> list[Any]:
    result = list(preview["lines"])
    if confirmed:
        result.extend(confirmed["lines"])
        result.extend([options["position"], confirmed["accepted"]])
    if preview["hit"] and confirmed:
        result.extend([preview["accepted"], confirmed["accepted"]])
    return result
