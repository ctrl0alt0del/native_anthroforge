"""An explicit current-shape edit and endpoint rebinding publish as one calculation result."""

from dataclasses import dataclass, replace
from typing import Any
from uuid import uuid4

from anthroforge.core.curve_engines import PolylineSettings
from anthroforge.core.entities import Attachment
from anthroforge.core.fibers import Fiber, FiberBinding
from anthroforge.core.results import EvaluationResult
from anthroforge.native import attachment_fields, construction, curve_editing, path_editing, paths

from . import attachment_assets
from .path_assets import PathAsset


@dataclass(frozen=True)
class EditGeometry:
    path: Any
    records: Any
    world: Any


def evaluate(
    engine: Any, item: Fiber, resources: Any, document: Any, world: Any, cancel: int
) -> Any:
    assert item.edit is not None
    asset = resources.attachments[item.attachment_asset]
    opening = resources.paths[item.edit.baseline].authored
    surfaces = attachment_assets.surface_inputs(engine, document, resources.meshes, asset.targets)
    current = attachment_assets.evaluate(engine, opening, asset, surfaces, world, cancel)
    path, records = edited_geometry(engine, current, opening, item, cancel)
    return recapture(engine, item, resources, document, EditGeometry(path, records, world), cancel)


def edited_geometry(engine: Any, current: Any, opening: Any, item: Fiber, cancel: int) -> Any:
    if item.edit is not None and not item.edit.shape:
        return current.path, construction.curve_records(current.authored)
    if item.engine != "ROUTED" and item.engine == opening.engine:
        return path_editing.rebase(current.path, opening, item, cancel)
    # Routed constraints are authored points; their connecting path is solved after rebinding.
    settings = PolylineSettings() if item.engine == "ROUTED" else item.engine_settings
    definition = replace(item, engine_settings=settings)
    records = construction.resolved_curve(engine, definition)
    return paths.evaluate(engine, definition, cancel, records), records


def capture_request(item: Fiber, path: Any, records: Any, world: Any) -> Any:
    assert item.edit is not None
    indices = {point.id: index for index, point in enumerate(item.points)}
    pins = [indices[b.point] for b in item.bindings]
    parents = [
        -1
        if b.attachment is not None
        and b.point in item.edit.rebind
        and b.capture_scope == "ANY_PARENT"
        else item.edit.candidates.index(b.target)
        for b in item.bindings
    ]
    return attachment_fields.Capture(path, records, world, pins, parents, retained_bindings(item))


def retained_bindings(item: Fiber) -> list[tuple[float, ...]]:
    assert item.edit is not None
    missing = (-1.0,) * 28
    return [
        missing if b.attachment is None or b.point in item.edit.rebind else b.attachment.binding
        for b in item.bindings
    ]


def recapture(
    engine: Any, item: Fiber, resources: Any, document: Any, geometry: EditGeometry, cancel: int
) -> Any:
    assert item.edit is not None
    path, records, world = geometry.path, geometry.records, geometry.world
    targets = item.edit.candidates
    surfaces = attachment_assets.surface_inputs(engine, document, resources.meshes, targets)
    field = attachment_fields.capture(
        engine, surfaces, capture_request(item, path, records, world), cancel
    )
    asset = attachment_assets.compact(field, targets)
    changed = edited_fiber(item, records, asset)
    return PathAsset(path, changed), changed, asset


def edited_fiber(item: Fiber, records: Any, asset: Any) -> Fiber:
    points = tuple(
        curve_editing.unpack(old, row) for old, row in zip(item.points, records, strict=True)
    )
    return replace(
        item,
        points=points,
        edit=None,
        attachment_asset=str(uuid4()),
        supports=asset.targets,
        bindings=captured_bindings(item, asset),
        result=EvaluationResult(),
    )


def captured_bindings(item: Fiber, asset: Any) -> tuple[FiberBinding, ...]:
    indices = {point.id: index for index, point in enumerate(item.points)}
    return tuple(captured(binding, indices[binding.point], asset) for binding in item.bindings)


def captured(before: FiberBinding, index: int, asset: Any) -> FiberBinding:
    row = asset.field.path.count + index * 3
    target = asset.targets[asset.field.owners[row, 0]]
    binding = tuple(asset.field.bindings[row, 0])
    return replace(
        before, target=target, attachment=Attachment(child_mode="OBJECT_ORIGIN", binding=binding)
    )
