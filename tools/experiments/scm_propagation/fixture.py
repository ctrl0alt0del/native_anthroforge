"""Capture immutable production inputs; numerical mapping stays in native code."""

from pathlib import Path
from types import SimpleNamespace as NS

import numpy as np

from anthroforge.application import attachment_assets, curve_sources, surface_providers
from anthroforge.application.storage import read_package
from anthroforge.native import components
from anthroforge.native.mesh import doubles

OUT = Path("build/scm-ribs-distortion/comparison")
TISSUE = "fc8df927-2290-4af2-b8e9-882697a8733e"


def state(engine, label):
    doc, res = read_package(Path("build/scm-ribs-distortion") / (label + ".anthroforge"), engine)
    return NS(engine=engine, document=doc, resources=res, assets=res.meshes)


def fixture(engine):
    before, after = state(engine, "before"), state(engine, "after")
    surface = after.document.object(after.document.object(TISSUE).source)
    values = [one(before, after, u.curve) for u in surface.curves]
    return NS(before=before, after=after, surface=surface, curves=values)


def parent_mesh(context, reference):
    value = surface_providers.get(context.engine, context.document, context.assets, reference)
    points = components.transformed(context.engine, value.resource.mesh.array(0), value.frame)
    return points, value.resource.mesh.array(3)


def parent_data(before, after, targets):
    first = []
    second = []
    counts = []
    for ref in targets:
        a, ta = parent_mesh(before, ref)
        b, tb = parent_mesh(after, ref)
        if a.shape != b.shape or not np.array_equal(ta, tb):
            raise ValueError("Regional experiment requires unchanged parent topology.")
        first.append(a)
        second.append(b)
        counts.append(len(a))
    return doubles(np.concatenate(first)), doubles(np.concatenate(second)), counts


def full_weights(field, indices, count):
    weights = np.zeros((len(field.owners), count))
    for slot in range(2):
        for old, new in enumerate(indices):
            mask = field.owners[:, slot] == old
            weights[mask, new] += field.weights[mask, slot]
    return doubles(weights)


def rest_points(context, item, field):
    data = np.concatenate((field.path.array()[:, :3], field.records[:, :9].reshape(-1, 3)))
    frame = curve_sources.world(context.engine, context.document, item.id)
    return doubles(components.transformed(context.engine, data, frame))


def one(before, after, key):
    item = before.document.object(key)
    asset = before.resources.attachments[item.attachment_asset]
    field = asset.field
    if item.engine != "POLYLINE" or field.path.count != len(item.points) or item.parent:
        raise ValueError("This fixture expects unparented, one-sample-per-point SCM polylines.")
    targets = tuple(dict.fromkeys(s.reference for s in asset.targets))
    data = NS(item=after.document.object(key), asset=asset, field=field, targets=targets)
    data.before, data.current, data.counts = parent_data(before, after, targets)
    return attach_capture(before, after, item, data)


def attach_capture(before, after, item, data):
    field, targets = data.field, data.targets
    positions = attachment_assets.resolved_points(
        after.engine, after.document, after.assets, data.asset, 0
    )
    data.pins = [
        next(i for i, p in enumerate(item.points) if p.id == b.point) for b in item.bindings
    ]
    indices = [targets.index(s.reference) for s in data.asset.targets]
    data.samples, data.points = field.path.count, rest_points(before, item, field)
    data.weights = full_weights(field, indices, len(targets))
    data.pin_parents = [targets.index(b.reference) for b in item.bindings]
    data.goals = doubles(positions[data.pins])
    return data
