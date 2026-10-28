"""Read-only access to retained skin evidence; no geometry work during inspection."""

import json
from typing import Any


def describe(session: Any) -> dict[str, Any]:
    return {name: stage(session, name) for name in ("envelope", "topology", "final")}


def stage(session: Any, name: str) -> dict[str, Any]:
    accepted = getattr(session.document.skin, name)
    data = session.resources.skin.get(accepted.data)
    if data is None:
        return {}
    info = json.loads(data.metadata)
    for row in info.get("budgets", ()):
        item = session.document.registry.records.get(row["owner"])
        row["label"] = item.name if item else row["owner"] or "Root remainder"
    return dict(
        revision=accepted.revision, geometry=accepted.asset, status=accepted.status, report=info
    )
