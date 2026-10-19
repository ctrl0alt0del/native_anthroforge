"""Authoritative result roles for construction-object dependency contracts."""

from .construction import Curve
from .objects import ObjectRecord
from .points import Anchor, Point
from .reference_images import ReferenceImage


def output(item: ObjectRecord) -> str:
    if isinstance(item, Point):
        return "binding" if isinstance(item, Anchor) else "point"
    if isinstance(item, Curve):
        return "path"
    return "image_resource" if isinstance(item, ReferenceImage) else "geometry"
