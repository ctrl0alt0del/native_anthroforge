"""Legacy FIELD construction owns its numerical fields and sampling policy."""

from typing import Any

from anthroforge.core.skin_field import decode
from anthroforge.native import skin_fields

from . import worker_memory
from .skin_draft_build import DraftRequest

TARGET_RESOLUTION = 220


def build(request: DraftRequest) -> tuple[Any, dict[str, Any]]:
    fields = prepare(request)
    try:
        result = request.scene.envelope(fields, worker_memory.budget(), request.cancel)
        details = dict(
            quality=result.diagnostics.report(), resolution=fields.resolution, voxel=fields.voxel
        )
        return result.mesh, details
    finally:
        fields.close()


def prepare(request: DraftRequest) -> Any:
    geometry = request.capture.geometry
    inputs = geometry.vertices, geometry.triangles, geometry.skeletal, request.capture.collagen
    config = decode(request.document.skin.draft_settings.configuration("FIELD"))
    options = config.settings, TARGET_RESOLUTION, worker_memory.budget(), request.cancel
    return skin_fields.prepare(request.engine, *inputs, *options, segments=geometry.segments)
