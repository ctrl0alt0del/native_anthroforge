"""Normal edits resolve retained material pins in workers; no nearest-target recapture."""

from dataclasses import replace
from typing import Any

import numpy as np

from anthroforge.native import curve_editing

from . import surface_providers


def prepare(
    engine: Any, document: Any, resources: Any, item: Any, world: Any, cancel: int, current: Any
) -> Any:
    if not item.edit or not item.edit.offsets:
        return item
    bindings = tuple(b for b in item.bindings if b.point in item.edit.offsets)
    goals = resolved_goals(engine, document, resources, bindings, cancel)
    indices = {p.id: i for i, p in enumerate(item.points)}
    source = replace(item, points=current.authored.points)
    return curve_editing.place(
        engine, source, [indices[b.point] for b in bindings], goals, world, cancel
    )


def resolved_goals(engine: Any, document: Any, resources: Any, bindings: Any, cancel: int) -> Any:
    result = np.empty((len(bindings), 3))
    groups = {(b.reference, b.material_asset) for b in bindings}
    for ref, asset in groups:
        provider = surface_providers.get(engine, document, resources.meshes, ref)
        indices = [
            i for i, b in enumerate(bindings) if (b.reference, b.material_asset) == (ref, asset)
        ]
        records = [bindings[i].attachment.binding for i in indices]
        frames = surface_providers.binding_frames(
            provider, resources.meshes, asset, records, cancel
        )
        result[indices] = frames.reshape((-1, 4, 4))[:, :3, 3]
    return result
