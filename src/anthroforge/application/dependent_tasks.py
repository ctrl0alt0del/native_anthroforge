"""One fan-out boundary for every evaluated output family."""

from typing import Any

from anthroforge.core.results import Port


def changed(session: Any, seeds: set[Port]) -> None:
    from . import construction_tasks, control_tasks, dependencies, path_tasks

    control_tasks.edited(session, seeds)
    path_tasks.edited(session, seeds)
    targets = dependencies.affected(session.document, seeds)
    targets -= {port.owner for port in seeds if port.output == "geometry"}
    construction_tasks.edited(session, targets)
