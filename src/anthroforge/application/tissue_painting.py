"""Read-only stroke previews and one topology-qualified authored commit."""

from typing import Any

from anthroforge.native import painting

from . import tissue_fields, tissue_strategy_operations
from . import tissue_inspection as inspection
from . import tissue_inspection_stages as stages
from .inspection_context import scene_signature


def field(context: Any, target: str, options: Any) -> Any:
    item = stages.tissue(context, target)
    value = next((f for f in item.fields if f.name == options.get("name")), None)
    if value is None:
        raise ValueError("Choose an existing tissue weight field.")
    tissue_fields.validate(context.resources, item, value.domain)
    return value


def validate(context: Any, target: str, options: Any) -> None:
    inspection.validate(context, target, options)
    field(context, target, options)
    if options["stage"] == "base":
        raise ValueError("Paint the rest, intrinsic or final tissue surface.")
    if len(options.get("samples", ())) not in range(1, 4097):
        raise ValueError("A paint stroke needs 1–4096 pointer samples.")


def obstacles(context: Any, options: Any) -> list[Any]:
    result = []
    for row in options.get("obstacles", ()):
        mesh = context.assets[row["asset"]].mesh
        result.append((mesh, tuple(row["frame"])))
    return result


def signature(context: Any, target: str, options: Any) -> Any:
    validate(context, target, options)
    inspection.expected_asset(context, target, options)
    return (
        scene_signature(context.document),
        target,
        stages.signature(context, target, options["stage"]),
        field(context, target, options),
        tuple((m.handle, frame) for m, frame in obstacles(context, options)),
    )


def prepare(context: Any, target: str, options: Any, cancel: int) -> Any:
    value = field(context, target, options)
    reference = stages.mesh(context, target, "rest") if value.domain == "REST" else None
    others = obstacles(context, options)
    inputs = painting.Inputs(
        stages.mesh(context, target, options["stage"]),
        reference,
        value.domain == "BASE",
        len(value.values),
        stages.instance_frame(context, target, options["stage"]),
        tuple(options["view"]),
        tuple(m for m, _ in others),
        tuple(f for _, f in others),
    )
    return painting.prepare(inputs, cancel)


def compute(context: Any, target: str, options: Any, cancel: int) -> dict[str, Any]:
    value = field(context, target, options)
    prepared = prepare(context, target, options, cancel)
    output = painting.PaintColors(
        prepared, value.values, options["samples"], options["brush"], cancel
    )
    report = dict(
        name=value.name,
        domain=value.domain,
        topology=value.topology,
        samples=len(options["samples"]),
        paint_through=bool(options["brush"][4]),
    )
    return dict(resource=output, report=dict(report, units="weight 0–1"))


def commit(session: Any, job: str) -> None:
    value = session.tissue_inspection.values.get("paint")
    require_current(session, value, job)
    result = value.asset
    weights = result["resource"].values.tolist()
    item = field(session, value.target, result["options"])
    if tuple(weights) != item.values:
        tissue_strategy_operations.field_set(session, value.target, item.name, weights, item.domain)
    inspection.cancel(session, "paint")


def require_current(session: Any, value: Any, job: str) -> None:
    if (
        not value
        or value.job != job
        or value.state != "ready"
        or not value.asset
        or not inspection.current(session, value.asset)
    ):
        raise ValueError("The stroke is incomplete or its inputs changed. Paint again.")
