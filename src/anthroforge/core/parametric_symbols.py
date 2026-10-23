"""Identity-preserving edits of equation text; numerical evaluation remains native."""

import re
from dataclasses import replace

from .parametric import ParametricSettings

IDENTIFIER = re.compile(r"\b[A-Za-z][A-Za-z0-9_]*\b", re.ASCII)


def reconcile(before: ParametricSettings, after: ParametricSettings) -> ParametricSettings:
    names = {v.id: v.name for v in after.variables}
    renamed = {v.name: names[v.id] for v in before.variables if v.id in names}
    removed = {v.name for v in before.variables if v.id not in names} - set(names.values())
    expressions = {
        axis: updated(getattr(before, axis), getattr(after, axis), renamed, removed)
        for axis in ("x", "y", "z")
    }
    interval = {
        name: updated(
            getattr(before.interval, name), getattr(after.interval, name), renamed, removed
        )
        for name in ("start_expression", "end_expression")
    }
    return with_expressions(after, expressions, interval)


def with_expressions(
    settings: ParametricSettings, coordinates: dict[str, str], interval: dict[str, str]
) -> ParametricSettings:
    bounds = replace(
        settings.interval,
        start_expression=interval["start_expression"],
        end_expression=interval["end_expression"],
    )
    return replace(
        settings, x=coordinates["x"], y=coordinates["y"], z=coordinates["z"], interval=bounds
    )


def updated(before: str, after: str, renamed: dict[str, str], removed: set[str]) -> str:
    if before == after:
        after = IDENTIFIER.sub(lambda match: renamed.get(match[0], match[0]), after)
    if removed.intersection(IDENTIFIER.findall(after)):
        raise ValueError("Resolve expression references before removing a Parametric variable.")
    return after
