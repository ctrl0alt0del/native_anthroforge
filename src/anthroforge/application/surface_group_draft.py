"""Review explicit source roles without publishing partial surface definitions."""

from typing import Any

from . import surface_grouping


def review(
    session: Any, curves: list[str], roles: dict[str, int], boundaries: dict[str, str]
) -> Any:
    records = session.document.registry.records
    main = [key for key in curves if roles.get(key, 0) == 0]
    numbers = sorted({value for value in roles.values() if value > 0})
    groups = [group(records, curves, roles, main, number, boundaries) for number in numbers]
    plan = dict(
        main=main, branches=[dict(boundary=g["boundary"], curves=g["curves"]) for g in groups]
    )
    reason = rejection(records, curves, plan)
    return dict(plan=plan, groups=groups, valid=not reason, reason=reason)


def rejection(records: Any, curves: Any, plan: Any) -> str:
    try:
        surface_grouping.checked(records, curves, plan)
        return ""
    except (KeyError, ValueError) as error:
        return (
            str(error) if isinstance(error, ValueError) else "Choose a connected outer main curve."
        )


def group(records: Any, curves: Any, roles: Any, main: Any, number: int, selected: Any) -> Any:
    children = [key for key in curves if roles.get(key) == number]
    possible = common_boundaries(records, children, main[:1] + main[-1:])
    boundary = selected.get(str(number), "")
    if boundary not in possible:
        boundary = possible[0] if possible else ""
    ordered = surface_grouping.ordered(records, boundary, children) if boundary else children
    return dict(
        number=number,
        curves=ordered,
        boundary=boundary,
        boundaries=[dict(id=k, name=records[k].name) for k in possible],
    )


def common_boundaries(records: Any, children: Any, candidates: Any) -> list[str]:
    links = surface_grouping.connections(records, list(dict.fromkeys([*children, *candidates])))
    return [
        key
        for key in dict.fromkeys(candidates)
        if all(key in links.get(child, ()) for child in children)
    ]
