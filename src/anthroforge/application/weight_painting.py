"""Shared scene inputs and commit qualification for native weight strokes."""

from typing import Any

from . import tissue_inspection as inspection


def obstacles(context: Any, options: Any) -> list[Any]:
    result = []
    for row in options.get("obstacles", ()):
        mesh = context.assets[row["asset"]].mesh
        result.append((mesh, tuple(row["frame"])))
    return result


def require_current(session: Any, value: Any, job: str) -> None:
    if (
        not value
        or value.job != job
        or value.state != "ready"
        or not value.asset
        or not inspection.current(session, value.asset)
    ):
        raise ValueError("The stroke is incomplete or its inputs changed. Paint again.")
