"""Owned envelope computation and binding resources, entirely on the coordinator worker."""

from dataclasses import asdict, dataclass
from typing import Any

from anthroforge.native import skin_fields, skin_gaps

from . import skin_assets, skin_capture, worker_memory

TARGET_RESOLUTION = 220


@dataclass(frozen=True)
class Envelope:
    mesh: Any
    data: skin_assets.SkinAsset


def evaluate(engine: Any, document: Any, resources: Any, cancel: int) -> Envelope:
    capture = skin_capture.capture(engine, document, resources, cancel)
    budget = worker_memory.budget()
    fields, scene = prepare(engine, document, capture, budget, cancel)
    try:
        result = scene.envelope(fields, budget, cancel)
        bindings = scene.bind(result.mesh, cancel)
        data = skin_assets.create(
            binding_data(bindings, capture), metadata(capture, result, fields)
        )
        return Envelope(result.mesh, data)
    finally:
        scene.close()
        fields.close()


def prepare(
    engine: Any, document: Any, capture: skin_capture.Capture, budget: int, cancel: int
) -> Any:
    geometry = capture.geometry
    field_inputs = geometry.vertices, geometry.triangles, geometry.skeletal, capture.collagen
    options = document.skin.envelope_settings, TARGET_RESOLUTION, budget, cancel
    fields = skin_fields.prepare(engine, *field_inputs, *options)
    try:
        source = geometry.vertices, geometry.triangles, geometry.owners, geometry.policies
        scene = skin_gaps.create(engine, *source, cancel)
        return fields, scene
    except Exception:
        fields.close()
        raise


def binding_data(bindings: dict[str, Any], capture: Any) -> dict[str, Any]:
    geometry = capture.geometry
    return bindings | dict(
        source_vertices=geometry.vertices,
        source_triangles=geometry.triangles,
        source_owners=geometry.owners,
    )


def metadata(capture: Any, result: Any, fields: Any) -> dict[str, Any]:
    return dict(
        kind="envelope_binding",
        sources=[source_metadata(row) for row in capture.sources],
        quality=result.diagnostics.report(),
        warnings=list(capture.warnings),
        resolution=fields.resolution,
        voxel=fields.voxel,
    )


def source_metadata(row: Any) -> dict[str, Any]:
    return dict(
        **asdict(row.identity),
        asset=row.asset,
        frame=row.frame,
        vertices=row.mesh.counts[0],
        triangles=row.mesh.counts[3],
    )
