"""Topology guides come from accepted source material, independently of presentation."""

from dataclasses import dataclass
from typing import Any

from anthroforge.core import skin_sources
from anthroforge.native import skin_guides

from . import mirror_surfaces, skin_capture, skin_inputs, skin_operations
from .object_frames import Frames


@dataclass(frozen=True)
class GuideSource:
    identity: skin_sources.Source
    data: skin_guides.Guides
    assets: tuple[str, ...]


@dataclass(frozen=True)
class Capture:
    sources: tuple[GuideSource, ...]
    warnings: tuple[str, ...]


def tissue(engine: Any, document: Any, resources: Any, source: Any, cancel: int) -> GuideSource:
    item = document.object(source.owner)
    state = item.rest_material
    if state is None or state.base_state.kind != "SURFACE":
        raise ValueError("No accepted surface material chart; use explicit FLOW Fibers.")
    base, current = resources.meshes[state.base].mesh, resources.meshes[state.rest].mesh
    frame = Frames(engine, document).world(item.id)
    frame = mirror_surfaces.frame(engine, document, skin_inputs.reference(source), frame)
    data = skin_guides.charts(base, current, frame, state.reverse, cancel)
    return GuideSource(source, data, (state.base, state.rest))


def fiber(engine: Any, document: Any, resources: Any, source: Any, cancel: int) -> GuideSource:
    accepted = skin_capture.fiber(engine, document, resources, source, cancel)
    data = skin_guides.path(accepted.mesh, accepted.frame, cancel)
    return GuideSource(source, data, (accepted.asset,))


def selected(document: Any, source: skin_sources.Source) -> bool:
    item = document.object(source.owner)
    if source.kind == "TISSUE":
        state = item.rest_material
        return bool((state.base_state if state is not None else item.base_state).kind == "SURFACE")
    return (
        source.kind == "FIBER"
        and not item.closed
        and skin_operations.settings_for(document.skin, source.owner).flow
    )


def capture(engine: Any, document: Any, resources: Any, cancel: Any) -> Capture:
    if document.skin.topology_settings.backend != "QUADWILD":
        return Capture((), ())
    output: list[GuideSource] = []
    warnings: list[str] = []
    for source in skin_sources.candidates(document):
        if not selected(document, source):
            continue
        if cancel.is_set():
            raise ValueError("Topology guide capture cancelled.")
        append(engine, document, resources, source, cancel, output, warnings)
    return Capture(tuple(output), tuple(warnings))


def append(
    engine: Any, document: Any, resources: Any, source: Any, cancel: Any, output: Any, warnings: Any
) -> None:
    try:
        evaluate = tissue if source.kind == "TISSUE" else fiber
        output.append(evaluate(engine, document, resources, source, cancel.handle))
    except (ValueError, KeyError) as error:
        if cancel.is_set():
            raise
        name = document.object(source.owner).name
        warnings.append(f"FLOW unavailable for {name} ({source.instance or 'source'}): {error}")
