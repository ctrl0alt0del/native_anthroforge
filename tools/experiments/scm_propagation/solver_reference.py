"""Compare direct conversion and an explicitly reduced endpoint-only solver reference."""

from dataclasses import replace

from regional_trial import library, parameters

from anthroforge.application import curve_evaluation, routing_evaluation
from anthroforge.application.path_assets import PathAsset
from anthroforge.core.curve_engines import RoutingSettings
from anthroforge.native import paths


def direct(context, data):
    item = replace(data.item, engine_settings=RoutingSettings(samples=data.samples))
    return curve_evaluation.evaluate_item(
        context.engine, context.document, context.resources, item, 0
    ).asset


def endpoint_curve(data):
    points = tuple(
        replace(data.item.points[i], position=tuple(goal))
        for i, goal in zip(data.pins, data.goals, strict=True)
    )
    return replace(data.item, points=points, engine_settings=RoutingSettings(samples=data.samples))


def endpoint(context, data, alignment, backend):
    item = endpoint_curve(data)
    warm = PathAsset(data.field.path, item)
    result = routing_evaluation.evaluate(
        context.engine, context.document, context.resources, item, 0, warm, backend
    )
    stations = [v[1] for v in alignment.stations]
    mapped = parameters(library(), result.path.array(1), stations)
    path = paths.restore(context.engine, result.path.array(), mapped, False)
    return PathAsset(path, data.item, result.diagnostics)
