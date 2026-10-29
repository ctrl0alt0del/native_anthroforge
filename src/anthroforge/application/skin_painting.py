"""Collagen strokes reuse native painting and revision-qualified inspection jobs."""

from typing import Any

import numpy as np

from anthroforge.core.scheduling import Workload
from anthroforge.core.skin import effective_collagen
from anthroforge.native import painting

from . import skin_collagen, skin_operations, surface_providers, weight_painting
from .inspection_context import scene_signature


def provider(context: Any, target: str) -> Any:
    skin_collagen.mesh(context, target)
    return surface_providers.get(context.engine, context.document, context.assets, target)


def validate(context: Any, target: str, options: Any) -> None:
    value = provider(context, target)
    if options.get("expected_asset", value.asset_id) != value.asset_id:
        raise ValueError("The displayed SCP changed. Paint its current surface again.")


def signature(context: Any, target: str, options: Any) -> Any:
    validate(context, target, options)
    return (
        scene_signature(context.document),
        skin_operations.settings_for(context.document.skin, target),
        tuple((m.handle, f) for m, f in weight_painting.obstacles(context, options)),
    )


def baseline(context: Any, target: str, mesh: Any) -> Any:
    setting = skin_operations.settings_for(context.document.skin, target)
    data = context.resources.skin.get(setting.painted)
    if setting.collagen_mode == "PAINTED" and skin_collagen.matching(data, mesh):
        return data.arrays["collagen"]
    value = effective_collagen(setting, context.document.object(target).name)
    return np.full(mesh.counts[0], value)


def prepare(context: Any, target: str, options: Any, cancel: int) -> Any:
    value = provider(context, target)
    mesh = value.resource.mesh
    others = weight_painting.obstacles(context, options)
    inputs = painting.Inputs(
        mesh,
        mesh,
        False,
        mesh.counts[0],
        value.frame,
        tuple(options["view"]),
        tuple(m for m, _ in others),
        tuple(f for _, f in others),
    )
    return painting.prepare(inputs, cancel)


def compute(context: Any, target: str, options: Any, cancel: int) -> dict[str, Any]:
    prepared = prepare(context, target, options, cancel)
    values = baseline(context, target, prepared.target)
    output = painting.PaintColors(prepared, values, options["samples"], options["brush"], cancel)
    report = dict(samples=len(options["samples"]), paint_through=bool(options["brush"][4]))
    return dict(resource=output, report=dict(report, units="collagen 0-1"))


def workload(context: Any, target: str, options: Any) -> Workload:
    return Workload(triangles=skin_collagen.mesh(context, target).counts[3])


def commit(session: Any, job: str) -> None:
    from .painting_compatibility import commit as apply

    apply(session, "collagen", job)
