"""Route the rest shape, recapture a native propagation field, then deform the parents."""

from dataclasses import replace
from types import SimpleNamespace as NS

import numpy as np
from fixture import attach_capture, parent_data

from anthroforge.application import attachment_assets, fiber_edit_evaluation
from anthroforge.application.attachment_candidates import eligible
from anthroforge.core.curve_engines import PolylineSettings
from anthroforge.core.fibers import FiberEdit


def recapture(before, after, original, routed):
    item = definition(before, original, routed)
    _, changed, asset = fiber_edit_evaluation.evaluate(
        before.engine, item, before.resources, before.document, item.matrix, 0
    )
    assert changed.bindings == original.bindings
    retain_captures(before, after, asset)
    return data(before, after, changed, asset)


def retain_captures(before, after, asset):
    for target in asset.targets:
        key = target.material_asset
        if key not in after.resources.meshes:
            after.resources.meshes[key] = before.resources.meshes[key]


def definition(before, original, routed):
    assert routed.path.count == len(original.points), "Compare matching 73-sample layouts."
    points = tuple(
        replace(p, position=tuple(row[:3]), left_mode="VECTOR", right_mode="VECTOR")
        for p, row in zip(original.points, routed.path.array(), strict=True)
    )
    return replace(
        original,
        points=points,
        engine_settings=PolylineSettings(),
        edit=FiberEdit(original.result.asset, eligible(before.document, original.id)),
    )


def data(before, after, item, asset):
    targets = tuple(dict.fromkeys(s.reference for s in asset.targets))
    value = NS(item=item, asset=asset, field=asset.field, targets=targets)
    value.before, value.current, value.counts = parent_data(before, after, targets)
    return attach_capture(before, after, item, value)


def current(after, value):
    positions = attachment_assets.resolved_points(
        after.engine, after.document, after.assets, value.asset, 0
    )
    return attachment_assets.evaluate(
        after.engine, value.item, value.asset, positions, value.item.matrix, 0
    )


def neutral(before, value, trial):
    positions = attachment_assets.resolved_points(
        before.engine, before.document, before.assets, value.asset, 0
    )
    ordinary = attachment_assets.evaluate(
        before.engine, value.item, value.asset, positions, value.item.matrix, 0
    )
    error = float(np.max(np.abs(ordinary.path.array()[:, :3] - value.field.path.array()[:, :3])))
    improved = trial.evaluate(value.before, value.points[value.pins])
    fit_error = float(np.max(np.abs(improved - value.points)))
    assert max(error, fit_error) < 1e-8
    return dict(current=error, improved=fit_error)
