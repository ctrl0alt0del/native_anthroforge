"""Worker-owned skin sources; presentation never chooses physical contributors."""

from dataclasses import dataclass
from typing import Any

import numpy as np

from anthroforge.core import skin_sources
from anthroforge.core.entities import IDENTITY
from anthroforge.core.skin import effective_collagen
from anthroforge.native import skin_capture as native
from anthroforge.native import tubes

from . import mirror_surfaces, skin_inputs, skin_operations, surface_providers
from .object_frames import Frames


@dataclass(frozen=True)
class Source:
    identity: skin_sources.Source
    mesh: Any
    frame: tuple[float, ...]
    asset: str


@dataclass(frozen=True)
class Capture:
    geometry: native.Capture
    sources: tuple[Source, ...]
    collagen: Any
    warnings: tuple[str, ...]


def surface(engine: Any, document: Any, resources: Any, source: skin_sources.Source) -> Source:
    provider = surface_providers.get(
        engine, document, resources.meshes, skin_inputs.reference(source)
    )
    return Source(source, provider.resource.mesh, provider.frame, provider.asset_id)


def fiber(engine: Any, document: Any, resources: Any, source: Any, cancel: int) -> Source | None:
    item = document.object(source.owner)
    setting = skin_operations.settings_for(document.skin, source.owner)
    if setting.fiber_radius == 0:
        return None
    if not item.result.asset or item.result.asset not in resources.paths or item.result.error:
        raise ValueError("Fiber has no accepted path for skin: " + item.name)
    frame = Frames(engine, document).world(item.id)
    frame = mirror_surfaces.frame(engine, document, skin_inputs.reference(source), frame)
    mesh = tubes.tube(
        resources.paths[item.result.asset].path, frame, setting.fiber_radius, cancel=cancel
    )
    return Source(source, mesh, IDENTITY, item.result.asset)


def sources(engine: Any, document: Any, resources: Any, cancel: int) -> tuple[Source, ...]:
    selected = skin_sources.selected(document, skin_sources.accepted_tissues(document))
    rows = [
        fiber(engine, document, resources, row, cancel)
        if row.kind == "FIBER"
        else surface(engine, document, resources, row)
        for row in selected
    ]
    result = tuple(row for row in rows if row is not None)
    if not result:
        raise ValueError("Skin needs accepted anatomy or fibers with a positive skin radius.")
    return result


def policy(document: Any, row: Source) -> tuple[float, float, bool]:
    setting = skin_operations.settings_for(document.skin, row.identity.owner)
    gap = setting if setting.gap_mode == "OVERRIDE" else document.skin.envelope_settings
    return gap.gap_limit_ratio, gap.gap_strength, row.identity.kind == "SCP"


def weights(document: Any, resources: Any, row: Source, warnings: list[str]) -> Any:
    count = row.mesh.counts[0]
    if row.identity.kind != "SCP":
        return np.ones(count)
    item = document.object(row.identity.owner)
    setting = skin_operations.settings_for(document.skin, item.id)
    if setting.collagen_mode == "PAINTED":
        asset = resources.skin.get(setting.painted)
        values = asset.arrays.get("collagen") if asset else None
        if values is not None and values.shape == (count,):
            return values
        warnings.append(
            "Painted collagen does not match " + item.name + "; using its uniform value."
        )
    return np.full(count, effective_collagen(setting, item.name))


def capture(engine: Any, document: Any, resources: Any, cancel: int = 0) -> Capture:
    rows = sources(engine, document, resources, cancel)
    geometry = native.capture(
        engine,
        [row.mesh for row in rows],
        [row.frame for row in rows],
        [policy(document, row) for row in rows],
        cancel,
    )
    warnings: list[str] = []
    collagen = np.concatenate([weights(document, resources, row, warnings) for row in rows])
    return Capture(geometry, rows, collagen, tuple(warnings))
