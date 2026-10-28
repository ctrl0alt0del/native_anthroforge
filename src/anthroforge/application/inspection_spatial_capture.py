"""Freeze optional spatial views against the same accepted revision as the report."""

import json
from typing import Any

from anthroforge.core.construction import finite

from . import inspection_neighborhood, tissue_inspection


def capture(session: Any, frozen: Any, settings: Any) -> None:
    from .inspection_report import capture_finding

    capture_finding(session, frozen, settings.get("finding"))
    for kind in ("measurements", "placement", "binding"):
        if settings.get(kind):
            current_query(session, frozen.view, kind)
    if settings.get("neighborhood"):
        neighborhood(session, frozen.view, settings)
    frozen.view.update(json.loads(json.dumps(frozen.view, allow_nan=False)))


def current_query(session: Any, view: Any, kind: str) -> None:
    status = tissue_inspection.status(session, kind)
    if status["state"] != "ready":
        raise ValueError("This inspection changed. Refresh it before exporting.")
    view[kind] = status["report"]


def neighborhood(session: Any, view: Any, settings: Any) -> None:
    row = inspection_neighborhood.describe(session, settings["neighborhood"])
    view["neighborhood"] = row
    if settings.get("camera"):
        finite(tuple(settings["camera"]), 7)
        view.update(
            camera=list(settings["camera"]), orthographic=bool(settings.get("orthographic"))
        )
