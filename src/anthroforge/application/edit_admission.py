"""Save admission shared by live sessions and isolated evaluation contexts."""

from typing import Any


def save_blocks_edits(context: Any) -> bool:
    if not context.waiting_save:
        return False
    coordinator = getattr(context, "scheduler", None)
    if coordinator is None:
        return True
    job = coordinator.registry.active.get(coordinator.publishing)
    return not (job is not None and job.writes and job.context == coordinator.context)
