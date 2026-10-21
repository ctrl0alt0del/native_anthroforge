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
    from . import stacking_inspection as stacking
    from . import tissue_inspection as tissue
    from . import tissue_painting as painting
    from . import tissue_sections as sections

    queries = dict(
        tissue_queries(),
        stacking=Query(stacking.validate, stacking.signature, stacking.compute, stacking.workload),
        paint=Query(painting.validate, painting.signature, painting.compute, tissue.workload),
        section=Query(sections.validate, sections.signature, sections.compute, sections.workload),
    )
    if kind not in queries:
        raise ValueError("Unknown inspection query kind.")
    return queries[kind]


def tissue_queries() -> dict[str, Query]:
    from . import tissue_inspection as tissue
    from . import tissue_point_inspection as point

    common = tissue.validate, tissue.signature
    return {
        "comparison": Query(*common, tissue.comparison, tissue.workload),
        "point": Query(*common, point.explain, tissue.workload),
    }
