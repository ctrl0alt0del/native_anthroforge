"""Parametric equations and variables use ordinary operations and one edit transaction."""

from dataclasses import asdict, replace
from typing import Any

from anthroforge.core.construction import Curve
from anthroforge.core.curve_engines import BezierSettings, decode
from anthroforge.core.parametric import ParametricSettings, Variable
from anthroforge.core.parametric import decode as decode_parametric
from anthroforge.core.parametric_symbols import reconcile

from . import object_operations


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
    config = reconcile(config, decode_parametric(values))
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
    updated = replace(
        config,
        variables=tuple(replace(v, **changes) if v.id == variable else v for v in variables),
    )
    object_operations.install(session, replace(item, engine_settings=reconcile(config, updated)))


def remove_variable(session: Any, curve: str, variable: str) -> None:
    item, config = current(session, curve)
    updated = replace(
        config,
        variables=tuple(v for v in config.variables if v.id != variable),
    )
    object_operations.install(session, replace(item, engine_settings=reconcile(config, updated)))


def switch(session: Any, item: Curve, engine: str) -> Curve:
    if engine == "PARAMETRIC":
        return restore_definition(session, item)
    asset = session.resources.paths.get(item.result.asset)
    if asset is None or asset.authored.engine != "PARAMETRIC":
        raise ValueError("Switching away requires an accepted Parametric path.")
    return replace(
        item,
        points=asset.authored.points,
        engine_settings=converted_settings(item, engine, len(asset.authored.points)),
        parametric_definition=settings(item),
    )


def restore_definition(session: Any, item: Curve) -> Curve:
    config = item.parametric_definition or ParametricSettings()
    return replace(item, engine_settings=config)


def converted_settings(item: Curve, engine: str, count: int) -> Any:
    if engine == "BEZIER" and settings(item).interpolation == "BEZIER":
        return BezierSettings(settings(item).bezier_resolution)
    return decode(engine, {"samples": max(64, count)} if engine == "ROUTED" else {})


def authored_copy(item: Curve) -> Curve:
    return replace(
        item, engine_settings=BezierSettings(resolution=item.resolution), parametric_definition=None
    )
