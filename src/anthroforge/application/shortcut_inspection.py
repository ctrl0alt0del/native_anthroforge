"""Shared read-only shortcut operation catalogue."""

from typing import Any

from . import (
    shortcut_effects,
    shortcut_formula_inspection,
    shortcut_policy_inspection,
    shortcut_progress,
)


def operations() -> dict[str, Any]:
    return {
        "shortcut.effects": shortcut_effects.inspect,
        "shortcut.formulas": shortcut_formula_inspection.inspect,
        "shortcut.attachment_policy": shortcut_policy_inspection.inspect,
        "shortcut.progress": shortcut_progress.inspect,
    }
