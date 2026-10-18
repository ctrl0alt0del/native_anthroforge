"""Category presentation policies, independent of anatomy and calculation quality."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .entities import Workspace

CATEGORIES = ("geometry", "curves", "points", "handles", "hooks", "cages", "anchors", "images")
PRESETS = {
    "all": ((), ()),
    "shape": (("anchors",), ("geometry",)),
    "surface": (("curves", "points", "handles", "hooks", "cages", "anchors"), ()),
    "attachments": (("curves", "points", "handles"), ("geometry",)),
}


def validate_categories(values: tuple[str, ...]) -> None:
    if set(values) - set(CATEGORIES) or len(values) != len(set(values)):
        raise ValueError("Unknown or duplicate presentation category.")


def visible(workspace: "Workspace", category: str) -> bool:
    return category not in workspace.hidden_categories


def pickable(workspace: "Workspace", category: str) -> bool:
    return visible(workspace, category) and category not in workspace.unpickable_categories
