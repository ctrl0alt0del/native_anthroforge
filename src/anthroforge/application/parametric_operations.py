"""Parametric equations and variables use ordinary operations and one edit transaction."""

from dataclasses import asdict, replace
from typing import Any

from anthroforge.core.construction import Curve
from anthroforge.core.curve_engines import BezierSettings, decode
from anthroforge.core.parametric import ParametricSettings, Variable
from anthroforge.core.parametric import decode as decode_parametric

from . import object_operations, parametric_policy


def current(session: Any, curve: str) -> tuple[Curve, ParametricSettings]:
    item = object_operations.editable(session, curve)
    if not isinstance(item, Curve) or item.engine != "PARAMETRIC":
        raise ValueError("Select a Parametric curve.")
    return item, settings(item)


def settings(item: Curve) -> ParametricSettings:
    if not isinstance(item.engine_settings, ParametricSettings):
        raise ValueError("Select a Parametric curve.")
    return item.engine_settings


def configure(session: Any, curve: str, changes: dict[str, Any]) -> None:
    item, config = current(session, curve)
    values = dict(asdict(config), **changes)
    if "interval" in changes:
        values["interval"] = dict(asdict(config.interval), **changes["interval"])
    config = decode_parametric(values)
    object_operations.install(session, replace(item, engine_settings=config))


def add_variable(session: Any, curve: str, name: str, **values: Any) -> str:
    item, config = current(session, curve)
    variable = Variable(name, **values)
    config = replace(config, variables=(*config.variables, variable))
    object_operations.install(session, replace(item, engine_settings=config))
    return variable.id


def update_variable(session: Any, curve: str, variable: str, changes: dict[str, Any]) -> None:
    item, config = current(session, curve)
    variables = config.variables
    if variable not in {v.id for v in variables} or "id" in changes:
        raise ValueError("Choose an existing variable; its identity cannot be changed.")
    config = replace(
        config,
        variables=tuple(replace(v, **changes) if v.id == variable else v for v in variables),
    )
    object_operations.install(session, replace(item, engine_settings=config))


def remove_variable(session: Any, curve: str, variable: str) -> None:
    item, config = current(session, curve)
    config = replace(
        config,
        variables=tuple(v for v in config.variables if v.id != variable),
    )
    object_operations.install(session, replace(item, engine_settings=config))


def switch(session: Any, item: Curve, engine: str) -> Curve:
    if engine == "PARAMETRIC":
        return restore_definition(session, item)
    asset = session.resources.paths.get(item.result.asset)
    if asset is None or asset.authored.engine != "PARAMETRIC":
        raise ValueError("Switching away requires an accepted Parametric path.")
    converted = decode(
        engine, {"samples": max(64, len(asset.authored.points))} if engine == "ROUTED" else {}
    )
    return replace(
        item,
        points=asset.authored.points,
        engine_settings=converted,
        parametric_definition=settings(item),
    )


def restore_definition(session: Any, item: Curve) -> Curve:
    config = item.parametric_definition or ParametricSettings()
    if any(p.junction for p in item.points) and len(item.points) != config.resolution:
        parametric_policy.require_resolution(session.document, item)
    return replace(item, engine_settings=config)


def authored_copy(item: Curve) -> Curve:
    return replace(item, engine_settings=BezierSettings(resolution=1), parametric_definition=None)
