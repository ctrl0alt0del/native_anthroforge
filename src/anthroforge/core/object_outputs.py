"""Authoritative result roles for construction-object dependency contracts."""

from .construction import Curve
from .objects import ConstructionObject
from .reference_images import ReferenceImage


def output(item: ConstructionObject) -> str:
    if isinstance(item, Curve):
        return "path"
    return "image_resource" if isinstance(item, ReferenceImage) else "geometry"
