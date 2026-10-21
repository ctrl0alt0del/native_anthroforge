"""Shared projection snapshots; image tracing creates no continuing relationship."""

from typing import TYPE_CHECKING, Any

from anthroforge.core.drawing import ProjectionSettings
from anthroforge.core.reference_images import ReferenceImage
from anthroforge.native import strokes

from . import curve_sources, surface_queries

if TYPE_CHECKING:
    from .session import Session


def project(
    session: "Session",
    rays: list[list[float]],
    plane: list[float] | None = None,
    surfaces: list[str] | None = None,
    image: str = "",
    settings: dict[str, Any] | None = None,
    interpolate: bool = True,
    mode: str = "PREVIEW",
) -> list[list[float]]:
    options = ProjectionSettings(**(settings or {}))
    depth = depth_plane(session, options, plane, image)
    return projected(session, rays, surfaces or [], options, depth, interpolate, mode)


def projected(
    session: Any, rays: Any, targets: Any, options: Any, depth: Any, interpolate: bool, mode: str
) -> list[list[float]]:
    inputs = surface_queries.inputs(
        session.engine,
        session.document,
        session.assets,
        targets,
        0,
        surface_queries.Mode[mode.upper()],
    )
    handles, frames = inputs
    stroke = strokes.Stroke(session.engine, handles, frames, depth, options.packed())
    stroke.batch(rays, interpolate)
    return list(stroke.read().tolist())


def depth_plane(
    session: "Session", options: ProjectionSettings, plane: list[float] | None, image: str
) -> list[float]:
    if options.depth != "IMAGE":
        if plane is None:
            raise ValueError("World drawing needs an explicit point/normal depth plane.")
        return plane
    if not isinstance(session.document.object(image), ReferenceImage):
        raise ValueError("Image-plane drawing requires a reference image.")
    frame = curve_sources.world(session.engine, session.document, image)
    return strokes.plane(session.engine, frame)
