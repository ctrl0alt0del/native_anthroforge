"""Accepted Fiber path input shared by topology guides and physical skin contributors."""

from dataclasses import dataclass
from typing import Any

from anthroforge.core import skin_sources

from . import mirror_surfaces, skin_inputs
from .object_frames import Frames


@dataclass(frozen=True)
class Source:
    identity: skin_sources.Source
    path: Any
    frame: tuple[float, ...]
    asset: str


def capture(engine: Any, document: Any, resources: Any, source: skin_sources.Source) -> Source:
    item = document.object(source.owner)
    if not item.result.asset or item.result.asset not in resources.paths or item.result.error:
        raise ValueError("Fiber has no accepted path for skin: " + item.name)
    frame = Frames(engine, document).world(item.id)
    frame = mirror_surfaces.frame(engine, document, skin_inputs.reference(source), frame)
    return Source(source, resources.paths[item.result.asset].path, frame, item.result.asset)
