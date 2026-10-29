"""Shared scene inputs and commit qualification for native weight strokes."""

from typing import Any


def obstacles(context: Any, options: Any) -> list[Any]:
    result = []
    for row in options.get("obstacles", ()):
        mesh = context.assets[row["asset"]].mesh
        result.append((mesh, tuple(row["frame"])))
    return result
