"""Owned envelope computation and binding resources, entirely on the coordinator worker."""

from typing import Any

from anthroforge.native import skin_gaps

from . import skin_assets, skin_capture
from .skin_builder_registry import BUILDERS as BUILDERS
from .skin_draft_build import CheckpointFailure, DraftRequest
from .skin_results import ComputedStage


def evaluate(engine: Any, document: Any, resources: Any, cancel: int) -> ComputedStage:
    capture = skin_capture.capture(engine, document, resources, cancel)
    scene = prepare_scene(engine, capture.geometry, cancel)
    try:
        return build(DraftRequest(engine, document, resources, cancel, capture, scene))
    finally:
        scene.close()


def build(request: DraftRequest) -> ComputedStage:
    key = request.document.skin.draft_settings.backend
    builder = BUILDERS[key]
    output = builder.build(request)
    try:
        bindings = request.scene.bind(output.mesh, request.cancel)
        info = (
            metadata(request.capture)
            | output.details
            | dict(builder=key, builder_version=builder.version)
        )
        asset = skin_assets.create(binding_data(bindings, request.capture), info)
        return ComputedStage(output.mesh, asset, checkpoints=output.checkpoints)
    except Exception as error:
        raise CheckpointFailure(error, output.checkpoints) from error


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
