"""Worker-owned contract shared by draft surface builders."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from anthroforge.core.document import Document
from anthroforge.native.mesh import GeometryEngine, Mesh
from anthroforge.native.skin_gaps import Scene

from .skin_capture import Capture
from .skin_checkpoint_assets import Bundle


@dataclass(frozen=True)
class DraftRequest:
    engine: GeometryEngine
    document: Document
    resources: Any
    cancel: int
    capture: Capture
    scene: Scene


@dataclass(frozen=True)
class DraftOutput:
    mesh: Mesh
    details: dict[str, Any]
    checkpoints: tuple[Bundle, ...] = ()


class CheckpointFailure(Exception):
    def __init__(self, error: Exception, checkpoints: tuple[Bundle, ...]):
        super().__init__(str(error))
        self.checkpoints = checkpoints


@dataclass(frozen=True)
class BuilderSettingsPolicy:
    configuration: Callable[..., Any]
    configure: Callable[..., Any]
    contributor: Callable[..., Any]
    configure_contributor: Callable[..., Any]
    contributor_fields: frozenset[str]
    effective: Callable[..., Any]
    resources: Callable[..., set[str]]


@dataclass(frozen=True)
class DraftBuilder:
    version: int
    build: Callable[[DraftRequest], DraftOutput]
    settings: BuilderSettingsPolicy
    inputs: Callable[..., Any]
    capture: Callable[..., Capture]
    reason: Callable[..., str]
    signature: Callable[..., tuple[str, ...]]
    worker_threads: int = 0
