"""Validate counterpart frames separately from shared source-reflected bindings."""

from typing import Any

from anthroforge.core.entities import SCP
from anthroforge.core.fibers import Fiber
from anthroforge.core.mirroring import SharedMirrorTarget
from anthroforge.core.points import Anchor
from anthroforge.native import measurement
from anthroforge.native.construction import matrix

from . import surface_providers


def binding(item: Any, key: str) -> tuple[Any, str]:
    if isinstance(item, Fiber):
        value = next(b for b in item.bindings if b.point == key)
        return value.attachment, value.material_asset
    if isinstance(item, Anchor):
        return item.binding.attachment, item.binding.material_asset
    return item.attachment, item.attachment.material_asset


def resolved_frame(context: Any, item: Any, key: str, ref: Any) -> Any:
    from .mirror_surfaces import frame

    settings, material = binding(item, key)
    if isinstance(item, SCP) and settings.parent_mode == "OBJECT_ORIGIN":
        return frame(
            context.engine, context.document, ref, context.document.entity(ref.target).matrix
        )
    if settings is None or not settings.binding:
        raise ValueError("The source binding has no accepted material position yet.")
    provider = surface_providers.get(context.engine, context.document, context.assets, ref)
    frames = surface_providers.binding_frames(
        provider, context.assets, material, [settings.binding], 0
    )
    return frames[0].tolist()


def validate(context: Any, instance: Any, rows: Any) -> list[dict[str, Any]]:
    document = context.document
    item = document.object(instance.source)
    return [checked(context, instance, item, row) for row in rows]


def checked(context: Any, instance: Any, item: Any, row: dict[str, Any]) -> dict[str, Any]:
    if shared(context.document, instance, row):
        return dict(row, binding_mode="source_reflection", surface_contact="not_checked")
    if needs_validation(context.document, instance, row):
        return measured(context, instance, item, row)
    return row


def shared(document: Any, instance: Any, row: Any) -> bool:
    return row["status"] == "mapped" and (
        SharedMirrorTarget(instance.source, row["binding"]) in document.shared_mirror_targets
    )


def needs_validation(document: Any, instance: Any, row: Any) -> bool:
    from anthroforge.core.mirroring import MirrorInstance

    if row["status"] != "mapped":
        return False
    plane = document.mirrors.plane(instance).frame
    return any(
        document.mirrors.plane(MirrorInstance(r["target"], r["instance"])).frame != plane
        for r in (row["reference"], row["mapped"])
        if r["instance"]
    )


def measured(context: Any, instance: Any, item: Any, row: Any) -> dict[str, Any]:
    from anthroforge.core.surface_references import SurfaceReference

    try:
        ref = SurfaceReference(**row["reference"])
        source = resolved_frame(context, item, row["binding"], ref)
        actual = resolved_frame(context, item, row["binding"], SurfaceReference(**row["mapped"]))
        expected = matrix(context.engine, context.document.mirrors.plane(instance).frame, source)
        return frame_residual(context, item, row, expected, actual)
    except ValueError as error:
        return dict(row, status="unavailable", error=str(error))


def frame_residual(context: Any, item: Any, row: Any, expected: Any, actual: Any) -> dict[str, Any]:
    residual = measurement.distance(context.engine, expected[3:12:4], actual[3:12:4])[3]
    normal = (
        0.0
        if isinstance(item, SCP) and item.attachment.parent_mode == "OBJECT_ORIGIN"
        else (measurement.distance(context.engine, expected[2:11:4], actual[2:11:4])[3])
    )
    return measured_row(row, residual, normal)


def measured_row(row: Any, residual: float, normal: float) -> dict[str, Any]:
    if residual > 1e-7 or normal > 1e-5:
        return dict(
            row,
            status="mismatch",
            residual=residual,
            normal_residual=normal,
            error="Reflected material anchor or normal differs from the retained target.",
        )
    return dict(row, residual=0.0)
