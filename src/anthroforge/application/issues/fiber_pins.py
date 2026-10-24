"""On-demand material-pin assessment proposes repairs without authoring them."""

from dataclasses import asdict
from typing import Any

from anthroforge.core.fibers import Fiber
from anthroforge.core.issues import Issue, evidence, fingerprint
from anthroforge.core.results import Port
from anthroforge.native import components, material_bindings, point_attachments
from anthroforge.native.mesh import NativeCancellation

from .. import attachment_assets, attachment_candidates, curve_sources, surface_providers
from ..construction_policy import revisions
from ..inspection_context import freeze
from .providers import Provider

NAME = "fiber_pins.v1"
REPAIR = "FIBER_PIN_REPAIR_AVAILABLE"


def scopes(document: Any) -> set[str]:
    return {o.id for o in document.objects if isinstance(o, Fiber) and o.result.asset}


def source(document: Any, scope: str) -> Any:
    item = document.registry.construction.get(scope)
    if not isinstance(item, Fiber):
        return None
    refs = set(attachment_candidates.eligible(document, scope))
    refs.update(b.reference for b in item.bindings if b.target in document.registry.anatomy)
    ports = surface_providers.ports(document, refs) | {Port(scope, "pose")}
    return dict(
        document=str(document.id),
        curve=scope,
        generation=item.generation,
        path=item.result.asset,
        inputs=[asdict(v) for v in revisions(document, ports)],
    )


def provider(session: Any) -> Provider:
    return Provider(
        NAME,
        scopes,
        lambda d, _: scopes(d),
        source,
        check,
        lambda _: freeze(session),
        lambda: NativeCancellation(session.engine),
        automatic=False,
    )


def request(session: Any, curves: list[str] | None = None) -> dict[str, str]:
    selected = scopes(session.document) if curves is None else set(curves)
    if not selected or selected - scopes(session.document):
        raise ValueError("Choose Fibers with accepted paths to check their pins.")
    session.issues.listening.invalidate(NAME, selected)
    session.issues.listening.synchronize()
    job = session.issues.listening.running.get(NAME)
    return dict(job=job.id if job else "", state="queued")


def check(context: Any, scope: str, cancel: Any) -> tuple[Issue, ...]:
    item = context.document.object(scope)
    if item.result.status == "pending":
        return ()
    invalid = invalid_pins(context, item, cancel)
    if not invalid:
        return ()
    positions = pin_positions(context, item, invalid)
    stamp = fingerprint(source(context.document, scope))
    return tuple(
        finding(context, item, index, position, stamp, cancel)
        for index, position in zip(invalid, positions, strict=True)
    )


def invalid_pins(context: Any, item: Fiber, cancel: Any) -> list[int]:
    invalid = {i for i, b in enumerate(item.bindings) if b.attachment is None}
    groups = {(b.reference, b.material_asset) for b in item.bindings if b.attachment}
    for ref, asset in groups:
        indices = matching_pins(item, ref, asset)
        invalid.update(invalid_group(context, item, indices, ref, asset, cancel))
    return sorted(invalid)


def matching_pins(item: Fiber, ref: Any, asset: str) -> list[int]:
    return [
        i
        for i, b in enumerate(item.bindings)
        if b.attachment and (b.reference, b.material_asset) == (ref, asset)
    ]


def invalid_group(
    context: Any, item: Fiber, indices: Any, ref: Any, asset: str, cancel: Any
) -> Any:
    try:
        valid = validate_group(context, item, indices, ref, asset, cancel.handle)
        return [i for i, flag in zip(indices, valid, strict=True) if not flag]
    except (ValueError, KeyError):
        if cancel.is_set():
            raise
        return indices


def validate_group(
    context: Any, item: Fiber, indices: Any, ref: Any, asset: str, cancel: int
) -> Any:
    provider = surface_providers.get(context.engine, context.document, context.assets, ref)
    reference = context.assets[asset or provider.asset_id].mesh
    records = [item.bindings[i].attachment.binding for i in indices]
    return material_bindings.validate(
        reference, provider.resource.mesh, provider.frame, records, cancel
    )


def pin_positions(context: Any, item: Fiber, indices: list[int]) -> Any:
    original = context.resources.paths[item.result.asset].authored
    points = {p.id: p.position for p in original.points}
    positions = [points[item.bindings[i].point] for i in indices]
    world = curve_sources.world(context.engine, context.document, item.id)
    return components.transformed(context.engine, positions, world)


def proposal(context: Any, item: Fiber, index: int, position: Any, cancel: int) -> dict[str, Any]:
    binding = item.bindings[index]
    targets = list(attachment_candidates.eligible(context.document, item.id))
    if binding.target in context.document.registry.anatomy:
        surface_providers.get(context.engine, context.document, context.assets, binding.reference)
        targets = [binding.reference]
    return capture_position(context, binding.point, targets, position, cancel)


def capture_position(
    context: Any, point: str, targets: Any, position: Any, cancel: int
) -> dict[str, Any]:
    meshes, frames = attachment_assets.surface_inputs(
        context.engine, context.document, context.assets, targets, cancel
    )
    owners, records = point_attachments.capture(
        context.engine, meshes, frames, [position], cancel=cancel
    )
    return proposed_binding(context, point, targets[int(owners[0])], records[0])


def proposed_binding(context: Any, point: str, ref: Any, record: Any) -> dict[str, Any]:
    resource = surface_providers.get(context.engine, context.document, context.assets, ref)
    return dict(
        point=point,
        target=ref.target,
        role=ref.role,
        binding=record.tolist(),
        material_asset=resource.asset_id,
    )


def finding(context: Any, item: Fiber, index: int, position: Any, stamp: str, cancel: Any) -> Issue:
    try:
        suggested = proposal(context, item, index, position, cancel.handle)
        details = "Review the proposed binding before applying; no authored state changed."
    except (ValueError, KeyError) as error:
        if cancel.is_set():
            raise
        suggested, details = None, str(error)
    return pin_issue(item, index, stamp, suggested, details)


def pin_issue(item: Fiber, index: int, stamp: str, suggested: Any, details: str) -> Issue:
    binding = item.bindings[index]
    fields: dict[str, Any] = dict(
        target=item.id, kind="FIBER", stage="binding", source=stamp, local_key=binding.point
    )
    payload = pin_evidence(binding, suggested)
    summary = f"{item.name}: binding {index + 1} needs repair"
    code = REPAIR if suggested else "FIBER_PIN_INVALID"
    return Issue(NAME, item.id, code, summary, details=details, evidence=payload, **fields)


def pin_evidence(binding: Any, suggested: Any) -> str:
    return evidence(
        point=binding.point, old_target=binding.target, old_role=binding.role, proposal=suggested
    )
