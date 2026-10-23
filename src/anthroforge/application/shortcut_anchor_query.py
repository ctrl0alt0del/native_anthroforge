"""Revision-qualified native anchor inspection on the shared read-only job service."""

from typing import Any

from anthroforge.core.scheduling import Workload

from . import shortcut_effects
from . import shortcut_policy_inspection as policies


def validate(context: Any, target: str, options: Any) -> None:
    shortcut_effects.selected(context, target)


def signature(context: Any, target: str, options: Any) -> Any:
    policy = policies.inspect(context, target)
    keys = {r["target"] for r in policy["rows"]}
    keys.update(context.document.entity(k).parent for k in tuple(keys))
    return (
        policy["policy"],
        policies.captured(context, target),
        tuple(context.document.entity(k) for k in sorted(keys - {""})),
    )


def workload(context: Any, target: str, options: Any) -> Workload:
    return Workload(affected=len(policies.inspect(context, target)["rows"]))


def compute(context: Any, target: str, options: Any, cancel: int) -> dict[str, Any]:
    return dict(report=policies.anchors(context, target))
