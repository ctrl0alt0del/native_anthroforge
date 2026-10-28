"""Optional candidate findings reuse the existing advisory check providers."""

from dataclasses import asdict
from typing import Any

from anthroforge.core.tissues import TissueVCP

from .inspection_context import InspectionContext
from .issues import surface_geometry, tissue_geometry


def inspect(context: Any) -> list[dict[str, Any]]:
    frozen = InspectionContext(
        context.document, context.resources, context.engine, context.document.workspaces[0]
    )
    rows = []
    for key in context.options.get("geometry_checks", ()):
        context.check_cancelled()
        rows.extend(check(frozen, key, context.cancel))
    return rows


def check(context: Any, key: str, cancel: Any) -> list[dict[str, Any]]:
    tissue = isinstance(context.document.object(key), TissueVCP)
    provider = tissue_geometry if tissue else surface_geometry
    stage = "final" if tissue else "geometry"
    return [asdict(issue) for issue in provider.check(context, key + ":" + stage, cancel)]
