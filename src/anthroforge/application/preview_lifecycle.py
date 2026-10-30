"""Bounded transient previews share cancellation and resource-release ownership."""

from functools import partial
from typing import Any

from . import painting, previews, tissue_inspection
from .painting_state import Painting
from .service_lifecycle import Event, Service

SLOTS = (
    "conversion",
    "mesh_replacement",
    "tissue_retarget",
    "surface_preview",
    "tissue_preview",
    "skin_fit_preview",
)


def attach(session: Any) -> Service:
    session.tissue_inspection = tissue_inspection.Inspection()
    session.painting = Painting()
    for slot in SLOTS:
        setattr(session, slot, previews.Preview())
    forget_queries(session)
    return Service(
        "previews",
        (
            (Event.INTERACTION_CANCEL, partial(painting.cancel, session)),
            (Event.CLEAR_PREVIEWS, partial(clear, session)),
            (Event.CLOSE, partial(close, session)),
        ),
    )


def clear(session: Any) -> None:
    painting.cancel(session)
    session.painting = Painting()
    for slot in SLOTS:
        previews.cancel(session, slot)
    session._editing.values.pop("component_read", None)
    session._editing.values.pop("query_revision", None)


def close(session: Any) -> None:
    clear(session)
    tissue_inspection.cancel(session)
    forget_queries(session)


def forget_queries(session: Any) -> None:
    for key in ("component_read", "query_revision", "inspection_snapshot"):
        session._editing.values.pop(key, None)
