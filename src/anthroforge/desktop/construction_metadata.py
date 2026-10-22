"""Construction presentation fields are queries over authored and workspace state."""

from dataclasses import asdict

from anthroforge.core import tissue_presets
from anthroforge.core.construction import Curve
from anthroforge.core.image_presentation import settings
from anthroforge.core.points import Point
from anthroforge.core.reference_images import ReferenceImage
from anthroforge.core.surfaces import Surface

from .curve_usage import users


def describe(session, item):
    from .point_scene import metadata

    result = dict(users=users(session.document, item.id), **metadata(session, item))
    if isinstance(item, (Point, Curve, Surface)):
        result["tissue_presets"] = tissue_presets.available(item)
    if isinstance(item, Curve):
        result["engine"] = item.engine
    if isinstance(item, ReferenceImage):
        result.update(
            source=item.source,
            dimensions=[item.width, item.height],
            image_style=asdict(settings(session.workspace, item.id)),
        )
    return result
