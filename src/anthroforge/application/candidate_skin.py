"""Optional position-only final-skin evaluation; no draft/topology/reference generation."""

from dataclasses import replace
from typing import Any

from anthroforge.core import skin_sources
from anthroforge.core.results import Port
from anthroforge.core.skeleton_update import Finding

from . import skin_deformation_evaluation, skin_jobs, skin_status, skin_update_tasks
from .assets import Asset
from .construction_policy import revisions


def assess(context: Any, changes: Any) -> dict[str, Any]:
    skin = context.document.skin
    reason = compatibility(context, changes)
    if skin.final.asset:
        invalidate(context, reason)
    result = dict(
        available=not reason, reason=reason, previewed=False, retained=bool(skin.final.asset)
    )
    if (
        context.options.get("preview_skin")
        and not reason
        and not any(f.blocking for f in context.findings)
    ):
        preview(context, result)
    return result


def compatibility(context: Any, changes: Any) -> str:
    owners = {r.owner for r in skin_sources.contributors(context.document)}
    changed = any(r.target in owners and r.correspondence != "verified" for r in changes)
    if context.document.skin.reference and changed:
        return "Replacement material correspondence changed; rebuild the skin reference explicitly."
    return str(skin_status.assess(context.document, context.resources).operations["update"].reason)


def invalidate(context: Any, reason: str) -> None:
    skin = context.document.skin
    result = replace(skin.final, status="invalid" if reason else "pending", error=reason)
    context.document = replace(context.document, skin=replace(skin, final=result))


def preview(context: Any, result: dict[str, Any]) -> None:
    port = Port(str(context.document.id), "skin_final")
    try:
        context.call(port, evaluate)
        result.update(previewed=True, retained=False)
    except (ValueError, RuntimeError) as error:
        context.check_cancelled()
        invalidate(context, str(error))
        context.findings.append(failure(context, str(error)))


def failure(context: Any, message: str) -> Finding:
    return Finding(
        "failure:skin", str(context.document.id), message, acknowledge=True, kind="failure"
    )


def evaluate(context: Any, port: Port) -> None:
    output = skin_deformation_evaluation.evaluate(
        context.engine, context.document, context.resources, context.cancel.handle
    )
    publish(context, output)
    context.prepared.add(port)


def publish(context: Any, output: Any) -> None:
    skin = context.document.skin
    reads = revisions(
        context.document, skin_update_tasks.inputs(context.resources, context.document)
    )
    stage = replace(
        skin_jobs.accepted(context.document, "final", output.data.digest, reads),
        revision=skin.final.revision + 1,
    )
    context.assets[stage.asset] = Asset(output.mesh, "generated", "", 1.0, False)
    context.resources.skin[output.data.digest] = output.data
    context.document = replace(context.document, skin=replace(skin, final=stage))
