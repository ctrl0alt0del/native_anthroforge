"""Retained target-relative goals consume shared providers without rewriting tissue sources."""

from typing import Any, cast

from anthroforge.native import binding_batches, components, point_attachments
from anthroforge.native.binding_batches import BindingBatch

from . import surface_providers, surface_queries, tissue_fields
from .object_frames import Frames


def capture(
    engine: Any, document: Any, resources: Any, item: Any, reference: Any, cancel: int
) -> Any:
    mesh = resources.meshes[item.rest_result.asset].mesh
    frame = Frames(engine, document).world(item.id)
    positions = components.transformed(engine, mesh.array(0), frame)
    provider = surface_providers.get(engine, document, resources.meshes, reference)
    surfaces = surface_queries.inputs(engine, document, resources.meshes, [reference], cancel)
    handles, frames = surfaces
    _, records = point_attachments.capture(engine, handles, frames, positions, cancel=cancel)
    _, signature = tissue_fields.mesh_domain(mesh)
    return BindingBatch(records), provider.asset_id, signature


def resolve(engine: Any, document: Any, resources: Any, item: Any, cancel: int) -> dict[str, Any]:
    rows = [r for r in item.constraints if r.reference is not None]
    if not rows:
        return {}
    domain = tissue_fields.domain(resources, item, "REST")
    frame = Frames(engine, document).world(item.id)
    return {r.id: goals(engine, document, resources, r, domain, frame, cancel) for r in rows}


def goals(
    engine: Any, document: Any, resources: Any, row: Any, domain: Any, frame: Any, cancel: int
) -> Any:
    batch = required_batch(resources, row, domain)
    provider = surface_providers.get(engine, document, resources.meshes, row.reference)
    frames = surface_providers.binding_frames(
        provider, resources.meshes, row.material_asset, batch.records, cancel
    )
    return binding_batches.positions(engine, frames, frame, row.offset, cancel)


def required_batch(resources: Any, row: Any, domain: Any) -> BindingBatch:
    batch = resources.bindings.get(row.binding_asset)
    if batch is None or len(batch.records) != domain[0] or row.topology != domain[1]:
        raise ValueError(
            "Target region no longer matches its rest topology; explicitly rebind or unlink it."
        )
    return cast(BindingBatch, batch)
