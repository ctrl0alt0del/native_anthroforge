"""Capture accepted construction inputs once at the coordinated base stage."""

from typing import Any

from anthroforge.core.fibers import Fiber
from anthroforge.core.membranes import Membrane
from anthroforge.core.points import Anchor
from anthroforge.core.tissue_base import TissueBaseState
from anthroforge.native import construction, tissue_inflation

from .consumed_paths import accepted as accepted_path
from .object_frames import Frames
from .tissue_output import TissueOutput


def capture(engine: Any, document: Any, resources: Any, item: Any, cancel: int) -> TissueOutput:
    source, frames = document.object(item.source), Frames(engine, document)
    frame = construction.matrix(engine, frames.world(item.id), frames.world(source.id), True)
    if isinstance(source, Anchor):
        require_result(source.result)
        frame = construction.matrix(engine, frames.world(item.id), source.resolved_frame, True)
        return TissueOutput(base=TissueBaseState("POINT", frame))
    if isinstance(source, Fiber):
        accepted_path(document, resources.paths, source.id)
        return TissueOutput(asset=source.result.asset, base=TissueBaseState("CURVE", frame))
    if isinstance(source, Membrane):
        return membrane(resources, item, source, frame, cancel)
    raise ValueError("Tissue requires attached construction.")


def require_result(result: Any) -> None:
    if not result.revision or result.status in ("failed", "invalid", "cancelled"):
        raise ValueError("Tissue construction has no usable accepted output.")


def membrane(resources: Any, item: Any, source: Any, frame: Any, cancel: int) -> TissueOutput:
    require_result(source.result)
    mesh = resources.meshes[source.result.asset].mesh
    if source.kind == "LOFT":
        mesh = tissue_inflation.refine(mesh, item.resolution, cancel)
    mesh = tissue_inflation.source(mesh, frame, cancel)
    return TissueOutput(mesh=mesh, base=TissueBaseState("SURFACE"))
