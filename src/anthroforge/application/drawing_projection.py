"""Shared projection snapshots; image tracing creates no continuing relationship."""

from typing import TYPE_CHECKING, Any

from anthroforge.core.drawing import ProjectionSettings
from anthroforge.core.reference_images import ReferenceImage
from anthroforge.native import strokes

from . import curve_sources

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
) -> list[list[float]]:
    options = ProjectionSettings(**(settings or {}))
    handles, frames = surface_inputs(session, surfaces or [])
    depth = depth_plane(session, options, plane, image)
    stroke = strokes.Stroke(session.engine, handles, frames, depth, options.packed())
    stroke.batch(rays, interpolate)
    return list(stroke.read().tolist())


def surface_inputs(session: "Session", targets: list[str]) -> tuple[list[int], list[Any]]:
    meshes, frames = [], []
    for key in dict.fromkeys(targets):
        item = session.document.entity(key)
        if not item.asset or item.asset not in session.assets:
            raise ValueError("Drawing surface needs accepted geometry.")
        meshes.append(session.assets[item.asset].mesh.handle)
        frames.append(curve_sources.world(session.engine, session.document, key))
    return meshes, frames


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
