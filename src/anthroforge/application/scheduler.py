"""Compatibility import for callers of the original scheduling API."""

from .coordinator import TaskCoordinator as Scheduler

__all__ = ["Scheduler"]
