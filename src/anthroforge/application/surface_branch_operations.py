"""Branch source groups use generic curves and explicit junction references."""

from dataclasses import replace
from typing import Any

from anthroforge.core.construction import Curve
from anthroforge.core.surface_branches import SurfaceBranch

from . import curve_consumers, curve_sources, object_operations, surface_operations


def add(session: Any, target: str, boundary: str, curves: list[str]) -> str:
    item = surface_operations.editable(session, target)
    if item.kind == "PATCH" or item.close_across:
        raise ValueError("Branches require an open main loft.")
    source = curve_sources.source(session.document, boundary)
    roots = tuple(
        shared_root(source, curve_sources.source(session.document, key)) for key in curves
    )
    branch = SurfaceBranch(boundary, tuple(curves), roots)
    uses = tuple(
        bound_use(session, item, key, root) for key, root in zip(curves, roots, strict=True)
    )
    object_operations.install(session, appended(item, branch, uses))
    return branch.id


def appended(item: Any, branch: SurfaceBranch, uses: tuple[Any, ...]) -> Any:
    return replace(
        item,
        kind="BRANCHED",
        main=item.main or tuple(u.curve for u in item.curves),
        branches=(*item.branches, branch),
        curves=(*item.curves, *uses),
        alignment=(),
        across=(),
    )


def shared_root(boundary: Curve, child: Curve) -> str:
    roots = {p.junction for p in boundary.points[1:-1] if p.junction}
    endpoints = {p.junction for p in (child.points[0], child.points[-1]) if p.junction}
    common = roots & endpoints
    if len(common) != 1:
        raise ValueError(
            "Each branch curve needs exactly one endpoint joined to an interior main point."
        )
    return common.pop()


def bound_use(session: Any, item: Any, curve: str, junction: str) -> Any:
    source = curve_sources.source(session.document, curve)
    use = curve_consumers.bind(session, item, curve)
    return replace(use, reverse=source.points[-1].junction == junction)


def remove(session: Any, target: str, branch: str) -> None:
    item = surface_operations.editable(session, target)
    selected = next((b for b in item.branches if b.id == branch), None)
    if selected is None:
        raise ValueError("Unknown surface branch.")
    branches = tuple(b for b in item.branches if b.id != branch)
    uses = tuple(u for u in item.curves if u.curve not in selected.curves)
    object_operations.install(session, detached(item, branches, uses))


def detached(item: Any, branches: tuple[SurfaceBranch, ...], uses: tuple[Any, ...]) -> Any:
    return replace(
        item,
        curves=uses,
        branches=branches,
        main=item.main if branches else (),
        kind="BRANCHED" if branches else "LOFT",
        alignment=(),
        across=(),
    )
