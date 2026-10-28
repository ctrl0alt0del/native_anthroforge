"""Projection invalidation follows ordinary transforms, separate from evaluation edges."""

from anthroforge.application.dependencies import closure
from anthroforge.core.entities import SCP

RELATIONSHIPS = frozenset(
    (
        "@membership",
        "parent",
        "follow",
        "owners",
        "bindings",
        "source",
        "curves",
        "primitive",
        "deformers",
        "name",
    )
)


def relationships_changed(changes):
    groups = (*changes.entities.values(), *changes.objects.values(), *changes.controls.values())
    return changes.reset or any(fields & RELATIONSHIPS for fields in groups)


def parent_edges(document):
    children = {}
    for item in document.registry.records.values():
        if isinstance(item, SCP):
            continue
        parent = getattr(item, "parent", "") or getattr(item, "follow", "")
        if parent:
            children.setdefault(parent, set()).add(item.id)
    return children


class ConstructionChanges:
    def __init__(self):
        self.children = {}

    def targets(self, document, changes, full):
        if full or relationships_changed(changes):
            self.children = parent_edges(document)
            return set(document.registry.authored)
        groups = (changes.entities, changes.controls, changes.objects)
        poses = {key for group in groups for key, fields in group.items() if "matrix" in fields}
        targets = set(changes.objects) | closure(self.children, poses)
        targets.update(
            item.id
            for item in document.registry.anatomy.values()
            if getattr(item, "source", "") in changes.objects
        )
        return targets
