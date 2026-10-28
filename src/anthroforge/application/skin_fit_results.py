"""Independent fitted-result inspection and lifecycle; preview never evaluates anatomy."""

import hashlib
import json
from dataclasses import asdict, replace
from typing import Any

from anthroforge.core.results import EvaluationResult

from .evaluation_results import matches


def definition_key(document: Any) -> str:
    from .skin_fit_jobs import definitions

    return hashlib.sha256(repr(definitions(document)).encode()).hexdigest()


def selected(session: Any, identity: str) -> Any:
    item = next((row for row in session.document.skin.fits if row.id == identity), None)
    if item is None:
        raise ValueError("Unknown fitted shortcut result.")
    return item


def inspect(session: Any, identity: str) -> dict[str, Any]:
    item = selected(session, identity)
    info = summary(session.resources.skin[item.data])
    current = matches(session.document, EvaluationResult(inputs=item.inputs))
    stale = item.stale or not current or item.definitions != definition_key(session.document)
    return dict(asdict(item), stale=stale, report=info)


def summary(data: Any) -> dict[str, Any]:
    info: dict[str, Any] = json.loads(data.metadata)
    background = int(info["settings"]["strategy"] == "SINGLE_ACTIVE")
    info["active_bones"] = data.arrays["weights"].shape[1] - background
    held_out = [row for row in info.get("rows", ()) if not row["training"]]
    info["moving_validation_p95"] = max(
        (row["moving_p95_percent_height"] for row in held_out), default=None
    )
    return info


def remove(session: Any, identity: str) -> None:
    selected(session, identity)
    skin = session.document.skin
    session.replace_document(
        skin=replace(skin, fits=tuple(f for f in skin.fits if f.id != identity))
    )


def refit_eligibility(session: Any, identity: str) -> dict[str, Any]:
    from . import skin_fit_capture

    try:
        item = inspect(session, identity)
        if item["report"]["settings"]["strategy"] != "SCALE_AWARE":
            raise ValueError("Refit Single Active results through the authoring operation.")
        return skin_fit_capture.describe(session, item["shortcut"])
    except (ValueError, KeyError) as error:
        return dict(available=False, reason=str(error), warnings=())
