"""Transport-independent painting operations and consumer availability."""

from collections.abc import Callable
from dataclasses import asdict
from functools import partial
from typing import Any

from anthroforge.core.painting import Brush

from . import painting
from .painting_consumers import consumer as definition


def execute(session: Any, operation: str, arguments: Any) -> Any:
    operations: dict[str, Callable[..., Any]] = {
        "describe": describe,
        "begin": painting.begin,
        "append": painting.append,
        "finish": painting.finish,
        "preview": painting.preview,
        "status": painting.status,
        "result": painting.result,
        "cancel": painting.cancel,
    }
    key = operation.removeprefix("painting.")
    if key not in operations:
        raise ValueError("Unknown painting operation: " + operation)
    return partial(operations[key], session)(**arguments)


def describe(session: Any, consumer: str, target: str, **options: Any) -> dict[str, Any]:
    reason = unavailable(session, consumer, target, options)
    return dict(
        consumer=consumer, target=target, available=not reason, reason=reason, **capabilities()
    )


def unavailable(session: Any, consumer: str, target: str, options: Any) -> str:
    reason = ""
    adapter = definition(consumer)
    try:
        adapter.require(session, target)
        adapter.validate(session, target, dict(options, stage=options.get("stage", "final")))
    except (KeyError, ValueError) as error:
        reason = str(error)
    return reason


def capabilities() -> dict[str, Any]:
    return dict(
        defaults=asdict(Brush()),
        radius_space="SCREEN",
        max_samples=4096,
        capabilities=["visibility", "paint_through", "scalar_values"],
        ranges=dict(radius=[1, 4096], weight=[0, 1], strength=[0, 1], falloff=[0.05, 20]),
    )
