"""One fan-out boundary for every evaluated output family."""

from typing import Any

from anthroforge.core.results import Port


def changed(session: Any, seeds: set[Port], published: bool = True) -> None:
    from . import construction_tasks, control_tasks, dependencies, output_tasks
    from .geometry_outputs import pending

    targets = dependencies.affected(session.document, seeds)
    if published:
        targets -= {port.owner for port in seeds if port.output == "geometry"}
    if targets:
        pending(session, targets)
    control_tasks.edited(session, seeds)
    output_tasks.edited(session, seeds)
    construction_tasks.schedule(session, targets)
