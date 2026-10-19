"""Construction presentation fields are queries over authored and workspace state."""

from dataclasses import asdict

from anthroforge.core import tissue_presets
from anthroforge.core.fibers import Fiber
from anthroforge.core.image_presentation import settings
from anthroforge.core.membranes import Membrane
from anthroforge.core.points import Anchor
from anthroforge.core.reference_images import ReferenceImage

from .curve_usage import users


def describe(session, item):
    from .point_scene import metadata

    result = dict(users=users(session.document, item.id), **metadata(session, item))
    if isinstance(item, (Anchor, Fiber, Membrane)):
        result["tissue_presets"] = tissue_presets.available(item)
    if isinstance(item, ReferenceImage):
        result.update(
            source=item.source,
            dimensions=[item.width, item.height],
            image_style=asdict(settings(session.workspace, item.id)),
        )
    return result
