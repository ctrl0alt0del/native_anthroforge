"""Query strategies share cancellation, snapshots and result lifetime in one job service."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Query:
    validate: Callable[..., Any]
    signature: Callable[..., Any]
    compute: Callable[..., Any]
    workload: Callable[..., Any]


def definition(kind: str) -> Query:
    queries = definitions()
    if kind not in queries:
        raise ValueError("Unknown inspection query kind.")
    return queries[kind]


def definitions() -> dict[str, Query]:
    from . import route_inspection as route
    from . import stacking_inspection as stacking
    from . import tissue_inspection as tissue
    from . import tissue_painting as painting
    from . import tissue_sections as sections

    return dict(
        dict(tissue_queries(), collagen=collagen_query()),
        stacking=Query(stacking.validate, stacking.signature, stacking.compute, stacking.workload),
        paint=Query(painting.validate, painting.signature, painting.compute, tissue.workload),
        section=Query(sections.validate, sections.signature, sections.compute, sections.workload),
        route=Query(route.validate, route.signature, route.compute, route.workload),
        shortcut=shortcut_query(),
    )


def shortcut_query() -> Query:
    from . import shortcut_anchor_query as shortcut

    return Query(shortcut.validate, shortcut.signature, shortcut.compute, shortcut.workload)


def tissue_queries() -> dict[str, Query]:
    from . import tissue_inspection as tissue
    from . import tissue_point_inspection as point

    common = tissue.validate, tissue.signature
    return {
        "comparison": Query(*common, tissue.comparison, tissue.workload),
        "point": Query(tissue.validate, point.signature, point.explain, tissue.workload),
    }


def collagen_query() -> Query:
    from . import skin_painting as collagen

    return Query(collagen.validate, collagen.signature, collagen.compute, collagen.workload)
