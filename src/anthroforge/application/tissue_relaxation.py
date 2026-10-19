"""Native relaxation captures explicit accepted sources and anatomical providers."""

from typing import Any

from anthroforge.core.points import Anchor
from anthroforge.native import construction, mesh_quality
from anthroforge.native import tissue_relaxation as native

from . import surface_providers, tissue_region_goals
from .object_frames import Frames
from .tissue_output import TissueOutput


def source(engine: Any, document: Any, resources: Any, item: Any) -> native.Source:
    value, base = native.Source(), item.base_state
    value.frame[:] = base.frame
    if base.kind == "SURFACE":
        value.mesh = resources.meshes[item.base_result.asset].mesh.handle
    elif base.kind == "CURVE":
        value.path = resources.paths[item.base_result.asset].path.handle
    elif base.kind == "POINT" and item.relaxation.mode == "GEOMETRIC":
        host(engine, document, resources, item, value)
    return value


def host(engine: Any, document: Any, resources: Any, item: Any, value: native.Source) -> None:
    anchor = document.object(item.source)
    if not isinstance(anchor, Anchor):
        raise ValueError("Point relaxation requires an attached Anchor source.")
    provider = surface_providers.get(engine, document, resources.meshes, anchor.binding.reference)
    value.host = provider.resource.mesh.handle
    frame = Frames(engine, document).world(item.id)
    value.host_frame[:] = construction.matrix(engine, frame, provider.frame, True)


def evaluate(engine: Any, document: Any, resources: Any, item: Any, cancel: int) -> TissueOutput:
    mesh = resources.meshes[item.rest_result.asset].mesh
    goals = tissue_region_goals.resolve(engine, document, resources, item, cancel)
    result, diagnostic = native.evaluate(
        mesh, source(engine, document, resources, item), item, cancel, goals
    )
    mesh_quality.validate(mesh, result, cancel)
    return TissueOutput(mesh=result, diagnostics=(diagnostic,))
