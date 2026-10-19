"""Construction presentation fields are queries over authored and workspace state."""

from dataclasses import asdict

from anthroforge.core.image_presentation import settings
from anthroforge.core.reference_images import ReferenceImage

from .curve_usage import users


def describe(session, item):
    from .point_scene import metadata

    result = dict(users=users(session.document, item.id), **metadata(session, item))
    if isinstance(item, ReferenceImage):
        result.update(
            source=item.source,
            dimensions=[item.width, item.height],
            image_style=asdict(settings(session.workspace, item.id)),
        )
    return result
