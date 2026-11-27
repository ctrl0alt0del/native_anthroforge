"""Constant-size identities for immutable skin inputs, independent of view state."""

from typing import Any


def key(document: Any) -> tuple[Any, ...]:
    return (
        document.id,
        document.entities,
        document.controls,
        document.objects,
        document.skin,
        document.mirror_rules,
        document.shared_mirror_targets,
        document.junctions,
        document.attachments_enabled,
        document.driving_shortcuts,
        document.formula_results,
        document.external_references,
    )


def resource_key(resources: Any) -> tuple[int, ...]:
    return id(resources), len(resources.meshes), len(resources.skin)
