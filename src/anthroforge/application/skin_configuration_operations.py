"""Authored pending settings and builder selection, without numerical side effects."""

from dataclasses import replace
from typing import Any

from . import skin_builder_configuration as builders


def configure(skin: Any, section: str, values: dict[str, Any]) -> Any:
    if section == "envelope_settings":
        return builders.configure(skin, "FIELD", values)
    changes = dict(values)
    backend = changes.pop("backend", skin.draft_settings.backend)
    builders.policy(backend)
    result = replace(skin, draft_settings=replace(skin.draft_settings, backend=backend))
    return builders.configure(result, backend, changes) if changes else result


def changed(before: Any, after: Any) -> Any:
    if before == after:
        return before
    applied = before.applied_draft
    pending = bool(applied and after.draft_settings.configuration() != applied.configuration)
    return replace(
        after, revision=before.revision + 1, construction_stale=before.construction_stale or pending
    )
