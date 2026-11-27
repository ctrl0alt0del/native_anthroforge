"""Worker-owned skin sources; presentation never chooses physical contributors."""

from dataclasses import asdict, dataclass
from typing import Any

from anthroforge.core import skin_sources
from anthroforge.native import skin_capture as native

from . import skin_inputs, surface_providers


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


def capture(engine: Any, document: Any, resources: Any, cancel: int = 0) -> Capture:
    from .skin_builder_registry import BUILDERS

    return BUILDERS[document.skin.draft_settings.backend].capture(
        engine, document, resources, cancel
    )


def geometry(engine: Any, rows: Any, policies: Any, cancel: int) -> Any:
    return native.capture_sources(
        engine,
        [row.mesh for row in rows],
        [0 for row in rows],
        [row.frame for row in rows],
        policies,
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
