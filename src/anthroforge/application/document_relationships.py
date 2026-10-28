"""Compose lifecycle policies for document-owned relationships before shared validation."""

from typing import Any

from . import assembly_retention, mirror_policy


def retain_settings(document: Any, changes: dict[str, Any]) -> dict[str, Any]:
    return assembly_retention.retained(document, mirror_policy.retain_settings(document, changes))
