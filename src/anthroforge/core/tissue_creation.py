"""Creation eligibility includes construction that can obtain independent anatomical binding."""

from .construction import Curve
from .fibers import Fiber
from .membranes import Membrane
from .points import Anchor, Point
from .surfaces import Surface


def domain(source: object) -> str:
    for cls, name in ((Point, "POINT"), (Curve, "CURVE"), (Surface, "SURFACE")):
        if isinstance(source, cls):
            return name
    raise ValueError("Select a Point, Curve or Surface to create tissue.")


def attached(source: object) -> bool:
    return isinstance(source, (Anchor, Fiber, Membrane))
