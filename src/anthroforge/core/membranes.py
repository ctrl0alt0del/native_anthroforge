"""Fiber-only surfaces share the generic Surface geometry and consumer contract."""

from dataclasses import dataclass

from .surfaces import Surface


@dataclass(frozen=True, slots=True)
class Membrane(Surface):
    """An attached surface; anchoring is inherited exclusively through its Fibers."""
