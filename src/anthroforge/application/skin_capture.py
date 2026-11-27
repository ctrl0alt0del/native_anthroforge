"""Worker-owned skin sources; presentation never chooses physical contributors."""

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from anthroforge.core import skin_sources
from anthroforge.core.skin import SkinContributor, effective_collagen
from anthroforge.native import skin_capture as native

from . import (
    skin_collagen,
    skin_inputs,
    skin_operations,
    surface_providers,
)


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


def sources(engine: Any, document: Any, resources: Any, cancel: int) -> tuple[Source, ...]:
    result = tuple(
        surface(engine, document, resources, row) for row in skin_sources.contributors(document)
    )
    if not result:
        raise ValueError("Skin needs accepted SCP or tissue surfaces.")
    return result


def policy(
    document: Any, row: Source, setting: SkinContributor | None = None
) -> tuple[float, float, bool]:
    setting = setting or skin_operations.settings_for(document.skin, row.identity.owner)
    gap = setting if setting.gap_mode == "OVERRIDE" else document.skin.envelope_settings
    return gap.gap_limit_ratio, gap.gap_strength, row.identity.kind == "SCP"


def weights(
    document: Any, resources: Any, row: Source, warnings: list[str], setting: SkinContributor
) -> Any:
    if row.identity.kind != "SCP":
        return np.ones(row.mesh.counts[0])
    item = document.object(row.identity.owner)
    if setting.collagen_mode == "PAINTED":
        asset = resources.skin.get(setting.painted)
        values = asset.arrays.get("collagen") if asset else None
        if skin_collagen.matching(asset, row.mesh):
            return values
        warnings.append(
            "Painted collagen does not match " + item.name + "; using its uniform value."
        )
    return np.full(row.mesh.counts[0], effective_collagen(setting, item.name))


def capture(engine: Any, document: Any, resources: Any, cancel: int = 0) -> Capture:
    rows = sources(engine, document, resources, cancel)
    lookup = {s.owner: s for s in document.skin.contributors}
    settings = [
        lookup.get(row.identity.owner) or SkinContributor(row.identity.owner) for row in rows
    ]
    geometry = captured_geometry(engine, document, rows, settings, cancel)
    if document.skin.draft_settings.backend == "AVBD":
        return Capture(geometry, rows, None, ())
    warnings: list[str] = []
    collagen = [
        weights(document, resources, row, warnings, setting)
        for row, setting in zip(rows, settings, strict=True)
    ]
    return Capture(geometry, rows, np.concatenate(collagen), tuple(warnings))


def captured_geometry(engine: Any, document: Any, rows: Any, settings: Any, cancel: int) -> Any:
    return native.capture_sources(
        engine,
        [row.mesh for row in rows],
        [0 for row in rows],
        [row.frame for row in rows],
        [policy(document, row, setting) for row, setting in zip(rows, settings, strict=True)],
        cancel,
    )


def source_metadata(row: Any) -> dict[str, Any]:
    counts = native.source_counts(row.mesh, False)
    return dict(
        **asdict(row.identity),
        asset=row.asset,
        frame=row.frame,
        vertices=counts[0],
        triangles=counts[1],
        segments=counts[2],
    )
