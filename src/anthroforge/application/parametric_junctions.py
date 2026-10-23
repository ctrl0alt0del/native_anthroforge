"""Formula-controlled junctions drive followers and reject contradictory equations."""

from typing import Any

from anthroforge.core.junctions import PointRef
from anthroforge.native.measurement import distance

TOLERANCE = 1e-8  # Metres, evaluated in the shared world frame.


def source(session: Any, references: list[PointRef]) -> PointRef:
    return next(
        (r for r in references if session.document.object(r.curve).engine == "PARAMETRIC"),
        references[0],
    )


def require_position(session: Any, item: Any, point: Any, world: Any) -> None:
    from .junction_edits import world_position

    current = world_position(session, item, point.id)
    if distance(session.engine, current, world)[3] > TOLERANCE:
        raise ValueError(
            "This junction position is formula-controlled; edit its Parametric variables."
        )


def validate(engine: Any, document: Any, resources: Any, item: Any) -> None:
    from . import curve_sources, junction_evaluation

    frame = curve_sources.world(engine, document, item.id)
    links = {j.id: j for j in document.junctions}
    for point in item.points:
        junction = links.get(point.junction)
        if junction and junction.source != PointRef(item.id, point.id):
            target = junction_evaluation.source_position(
                engine, document, resources, item.id, junction.source
            )
            a, b = engine.world_point(frame, point.position), engine.world_point(frame, target)
            if distance(engine, a, b)[3] > TOLERANCE:
                raise ValueError("Parametric junction equations disagree; accepted path retained.")
