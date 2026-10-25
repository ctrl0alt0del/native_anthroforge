"""Portable descriptions of changes requiring explicit replacement review."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Change:
    key: str
    target: str
    action: str
    description: str
