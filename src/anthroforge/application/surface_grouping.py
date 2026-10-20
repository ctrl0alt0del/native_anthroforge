"""Infer open branch groups from explicit identities, never geometric proximity."""

from dataclasses import replace
from itertools import product
from typing import Any

from anthroforge.core.curve_uses import CurveUse
from anthroforge.core.object_registry import validate_sources
from anthroforge.core.surface_branches import SurfaceBranch
from anthroforge.core.surfaces import Surface

from . import curve_sources, surface_branch_operations


def connections(records: Any, curves: list[str]) -> dict[str, list[str]]:
    incoming: dict[str, list[str]] = {}
    for child in curves:
        for boundary in curves:
            if child == boundary or records[child].closed or records[boundary].closed:
                continue
            try:
                surface_branch_operations.shared_root(records[boundary], records[child])
                incoming.setdefault(child, []).append(boundary)
            except ValueError:
                continue
    return incoming


def partitions(values: list[str]) -> Any:
    if not values:
        yield []
    for count in range(len(values), 1, -1):
        for rest in partitions(values[count:]):
            yield [values[:count], *rest]


def ordered(records: Any, boundary: str, children: list[str]) -> list[str]:
    roots = {p.junction: i for i, p in enumerate(records[boundary].points) if p.junction}
    return sorted(
        children,
        key=lambda key: roots[
            surface_branch_operations.shared_root(records[boundary], records[key])
        ],
    )


def group_plans(records: Any, main: list[str], grouped: Any) -> Any:
    groups = [(key, ordered(records, key, values)) for key, values in grouped.items()]
    if any(not distinct_roots(records, key, values) for key, values in groups):
        return
    for branches in group_combinations(groups):
        yield dict(main=main, branches=branches)


def distinct_roots(records: Any, key: str, values: list[str]) -> bool:
    roots = [surface_branch_operations.shared_root(records[key], records[v]) for v in values]
    return len(roots) >= 2 and len(set(roots)) == len(roots)


def group_combinations(groups: Any) -> Any:
    if not groups:
        yield []
        return
    key, values = groups[0]
    for parts in partitions(values):
        for rest in group_combinations(groups[1:]):
            yield [*(dict(boundary=key, curves=children) for children in parts), *rest]


def candidate_plans(records: Any, curves: list[str], incoming: Any) -> Any:
    main = [key for key in curves if key not in incoming]
    children = list(incoming)
    choices = [
        [key for key in incoming[child] if key in (main[:1] + main[-1:])] for child in children
    ]
    if len(main) < 2 or any(not choice for choice in choices):
        return
    for number, assignment in enumerate(product(*choices)):
        if number == 256:
            yield None
            return
        grouped = assigned_groups(children, assignment)
        yield from group_plans(records, main, grouped)


def assigned_groups(children: Any, assignment: Any) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {}
    for child, boundary in zip(children, assignment, strict=True):
        grouped.setdefault(boundary, []).append(child)
    return grouped


def apply(item: Any, plan: Any, records: Any) -> Any:
    branches = tuple(branch_record(records, value) for value in plan["branches"])
    result = replace(item, **grouped_values(item, plan, branches, records))
    validate_sources(result, records)
    return result


def grouped_values(item: Any, plan: Any, branches: Any, records: Any) -> dict[str, Any]:
    return dict(
        kind="BRANCHED" if branches else item.kind,
        main=tuple(plan["main"]) if branches else (),
        branches=branches,
        curves=oriented_uses(item, plan, branches, records),
        alignment=(),
        across=(),
    )


def oriented_uses(item: Any, plan: Any, branches: Any, records: Any) -> tuple[Any, ...]:
    uses = {use.curve: use for use in item.curves}
    ordered_uses = [uses[key] for key in plan["main"]]
    for branch in branches:
        ordered_uses.extend(
            replace(uses[key], reverse=records[key].points[-1].junction == root)
            for key, root in zip(branch.curves, branch.junctions, strict=True)
        )
    return tuple(ordered_uses)


def branch_record(records: Any, value: Any) -> SurfaceBranch:
    boundary, curves = value["boundary"], value["curves"]
    return SurfaceBranch(
        boundary,
        tuple(curves),
        tuple(
            surface_branch_operations.shared_root(records[boundary], records[key]) for key in curves
        ),
    )


def checked(records: Any, curves: list[str], plan: Any) -> Any:
    keys = plan["main"] + [key for group in plan["branches"] for key in group["curves"]]
    if len(keys) != len(set(keys)) or set(keys) != set(curves):
        raise ValueError("Every selected curve must belong to exactly one group.")
    item = Surface(curves=tuple(CurveUse(key) for key in curves))
    apply(item, plan, records)
    return plan


def infer(session: Any, curves: list[str]) -> dict[str, Any]:
    records = {key: curve_sources.source(session.document, key) for key in curves}
    incoming = connections(records, curves)
    if not incoming:
        return dict(ambiguous=False, plan=checked(records, curves, dict(main=curves, branches=[])))
    return discover(records, curves, incoming)


def discover(records: Any, curves: list[str], incoming: Any) -> dict[str, Any]:
    found: list[dict[str, Any]] = []
    for plan in candidate_plans(records, curves, incoming):
        if plan is None:
            return dict(ambiguous=True, plan=found[0] if found else suggested(curves, incoming))
        if valid_plan(records, curves, plan):
            found.append(plan)
        if len(found) == 2:
            break
    if not found:
        raise ValueError(INVALID_GROUPS)
    return dict(ambiguous=len(found) > 1, plan=found[0])


INVALID_GROUPS = (
    "Connections need two main curves and two distinct interior roots per branch. "
    "Closed, nested and overlapping branches are unsupported."
)


def suggested(curves: list[str], incoming: Any) -> dict[str, Any]:
    main = [key for key in curves if key not in incoming]
    groups: dict[str, list[str]] = {}
    for key, parents in incoming.items():
        groups.setdefault(parents[0], []).append(key)
    return dict(main=main, branches=[dict(boundary=k, curves=v) for k, v in groups.items()])


def valid_plan(records: Any, curves: list[str], plan: Any) -> bool:
    try:
        checked(records, curves, plan)
        return True
    except ValueError:
        return False


def inspect(session: Any, curves: list[str]) -> dict[str, Any]:
    result = infer(session, curves)
    return dict(result, curves=[dict(id=k, name=session.document.object(k).name) for k in curves])
