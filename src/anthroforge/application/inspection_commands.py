"""Explicit presentation operations shared by desktop and headless inspection."""

from typing import Any

from . import (
    binding_inspection,
    bookmarks,
    inspection_neighborhood,
    measurements,
    spatial_evidence,
    tissue_inspection,
)
from .issues import surface_geometry
from .session import Session

OPERATIONS = {
    "geometry.check": surface_geometry.request,
    "geometry.finding": spatial_evidence.issue,
    "geometry.measure": lambda session, **options: tissue_inspection.start(
        session, "measurements", **options
    ),
    "geometry.measure.status": lambda session: tissue_inspection.status(session, "measurements"),
    "geometry.neighborhood": inspection_neighborhood.describe,
    "geometry.placement": lambda session, **options: tissue_inspection.start(
        session, "placement", **options
    ),
    "geometry.placement.status": lambda session: tissue_inspection.status(session, "placement"),
    "geometry.binding.options": binding_inspection.bindings,
    "geometry.binding": lambda session, **options: tissue_inspection.start(
        session, "binding", **options
    ),
    "geometry.binding.status": lambda session: tissue_inspection.status(session, "binding"),
    "measurement.point": measurements.point,
    "measurement.add": measurements.add,
    "measurement.remove": measurements.remove,
    "measurement.list": measurements.inspect,
    "bookmark.add": bookmarks.add,
    "bookmark.restore": bookmarks.restore,
    "bookmark.rename": bookmarks.rename,
    "bookmark.remove": bookmarks.remove,
    "bookmark.list": bookmarks.inspect,
}


def execute(session: Session, operation: str, arguments: dict[str, Any]) -> Any:
    if operation not in OPERATIONS:
        raise ValueError("Unknown inspection operation: " + operation)
    return OPERATIONS[operation](session, **arguments)  # type: ignore[operator]
