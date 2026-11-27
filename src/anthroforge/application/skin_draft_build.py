"""Worker-owned contract shared by draft surface builders."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from anthroforge.core.document import Document
from anthroforge.native.mesh import GeometryEngine, Mesh
from anthroforge.native.skin_gaps import Scene

from .skin_capture import Capture


@dataclass(frozen=True)
class DraftRequest:
    engine: GeometryEngine
    document: Document
    resources: Any
    cancel: int
    capture: Capture
    scene: Scene


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
    build: Callable[[DraftRequest], tuple[Mesh, dict[str, Any]]]
    settings: BuilderSettingsPolicy
    inputs: Callable[..., Any]
    capture: Callable[..., Capture]
    reason: Callable[..., str]
    signature: Callable[..., tuple[str, ...]]
