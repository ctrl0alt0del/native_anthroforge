"""Owned envelope computation and binding resources, entirely on the coordinator worker."""

from typing import Any

from anthroforge.native import skin_fields, skin_gaps

from . import skin_assets, skin_avbd, skin_capture, worker_memory
from .skin_draft_build import DraftBuilder, DraftRequest
from .skin_results import ComputedStage

TARGET_RESOLUTION = 220


def evaluate(engine: Any, document: Any, resources: Any, cancel: int) -> ComputedStage:
    capture = skin_capture.capture(engine, document, resources, cancel)
    scene = prepare_scene(engine, capture.geometry, cancel)
    try:
        key = document.skin.draft_settings.backend
        builder = BUILDERS[key]
        mesh, details = builder.build(
            DraftRequest(engine, document, resources, cancel, capture, scene)
        )
        bindings = scene.bind(mesh, cancel)
        info = metadata(capture) | details | dict(builder=key, builder_version=builder.version)
        return ComputedStage(mesh, skin_assets.create(binding_data(bindings, capture), info))
    finally:
        scene.close()


def field_surface(request: DraftRequest) -> tuple[Any, dict[str, Any]]:
    capture = request.capture
    geometry = capture.geometry
    inputs = geometry.vertices, geometry.triangles, geometry.skeletal, capture.collagen
    budget = worker_memory.budget()
    options = request.document.skin.envelope_settings, TARGET_RESOLUTION, budget, request.cancel
    fields = skin_fields.prepare(request.engine, *inputs, *options, segments=geometry.segments)
    try:
        result = request.scene.envelope(fields, budget, request.cancel)
        details = dict(
            quality=result.diagnostics.report(), resolution=fields.resolution, voxel=fields.voxel
        )
        return result.mesh, details
    finally:
        fields.close()


BUILDERS = {"FIELD": DraftBuilder(1, field_surface), "AVBD": DraftBuilder(3, skin_avbd.build)}


def binding_data(bindings: dict[str, Any], capture: Any) -> dict[str, Any]:
    geometry = capture.geometry
    return bindings | dict(
        source_vertices=geometry.vertices,
        source_triangles=geometry.triangles,
        source_owners=geometry.owners,
        source_segments=geometry.segments,
        source_segment_owners=geometry.segment_owners,
    )


def metadata(capture: Any) -> dict[str, Any]:
    return dict(
        kind="envelope_binding",
        sources=[skin_capture.source_metadata(row) for row in capture.sources],
        warnings=list(capture.warnings),
    )


def prepare_scene(engine: Any, geometry: Any, cancel: int) -> Any:
    source = geometry.vertices, geometry.triangles, geometry.owners, geometry.policies
    return skin_gaps.create(engine, *source, cancel, geometry.segments, geometry.segment_owners)
