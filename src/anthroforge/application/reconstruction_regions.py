"""Named material patches retain their original domain; changed topology needs explicit repair."""

from dataclasses import asdict, replace
from typing import Any

from anthroforge.core.reconstruction import SurfaceRegion
from anthroforge.core.surface_references import SurfaceReference

from . import reconstruction_state as records
from . import surface_providers
from .field_domains import mesh_domain
from .operations import require_name


def provider(session: Any, target: str, role: str, variant: str) -> Any:
    document = records.scene(session, variant)
    return surface_providers.get(
        session.engine, document, session.assets, SurfaceReference(target, role)
    )


def view_arguments(session: Any, view: Any, name: str, triangles: Any) -> Any:
    from anthroforge.core.tissues import TissueVCP

    item = view.source.document.object(view.subject)
    role = "SCP_GEOMETRY"
    if isinstance(item, TissueVCP):
        role = "TISSUE_BASE" if view.stage == "base" else "TISSUE_FINAL"
    current = provider(session, view.subject, role, view.variant)
    if len(view.layers) != 1 or current.resource.mesh is not view.layers[0].resource:
        raise ValueError("Choose the current Base or Final surface and refresh this comparison.")
    return dict(
        name=name, target=view.subject, role=role, variant=view.variant, triangles=triangles
    )


def set_region(session: Any, name: str, target: str, triangles: Any, **options: Any) -> str:
    if set(options) - {"role", "variant", "region"}:
        raise ValueError("Unknown region setting.")
    role, variant, region = (
        options.get(k, d) for k, d in (("role", "SCP_GEOMETRY"), ("variant", ""), ("region", ""))
    )
    records.subject(session, target, variant)
    surface = provider(session, target, role, variant)
    selected = validate_triangles(surface, triangles)
    _, topology = mesh_domain(surface.resource.mesh)
    row = SurfaceRegion(
        require_name(name), target, role, topology, selected, surface.asset_id, variant
    )
    return save_region(session, row, region)


def validate_triangles(surface: Any, triangles: Any) -> tuple[int, ...]:
    selected = tuple(sorted(set(triangles)))
    if not selected or any(
        type(i) is not int or i < 0 or i >= surface.resource.mesh.counts[3] for i in selected
    ):
        raise ValueError("Select existing surface triangles for the region.")
    return selected


def save_region(session: Any, row: SurfaceRegion, region: str) -> str:
    if region:
        records.selected(session, "regions", region)
        row = replace(row, id=region)
    return str(records.upsert(session, "regions", row))


def inspect(session: Any, region: str) -> dict[str, Any]:
    row = records.selected(session, "regions", region)
    try:
        surface = provider(session, row.target, row.role, row.variant)
        valid = mesh_domain(surface.resource.mesh)[1] == row.topology
        reason = "" if valid else "Surface topology/material domain changed; redefine this region."
    except ValueError as error:
        valid, reason = False, str(error)
    return dict(asdict(row), available=valid, reason=reason)


def remove(session: Any, id: str) -> None:
    state = records.state(session)
    if any(id in c.members for c in state.collections) or any(
        r.region == id for r in state.reviews
    ):
        raise ValueError("This region is used by a collection or review history.")
    records.remove(session, "regions", id)
