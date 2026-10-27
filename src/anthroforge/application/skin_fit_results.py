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
    info = json.loads(session.resources.skin[item.data].metadata)
    current = matches(session.document, EvaluationResult(inputs=item.inputs))
    stale = item.stale or not current or item.definitions != definition_key(session.document)
    return dict(asdict(item), stale=stale, report=info)


def remove(session: Any, identity: str) -> None:
    selected(session, identity)
    skin = session.document.skin
    session.replace_document(
        skin=replace(skin, fits=tuple(f for f in skin.fits if f.id != identity))
    )
