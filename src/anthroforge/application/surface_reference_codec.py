"""Explicit surface identities and immutable material capture ownership in project records."""

from dataclasses import replace
from typing import Any

from anthroforge.core.surface_references import CapturedSurface, SurfaceReference


def capture(data: Any) -> CapturedSurface:
    return CapturedSurface(SurfaceReference(**data["reference"]), data["material_asset"])


def remap(ref: SurfaceReference, identities: dict[str, str]) -> SurfaceReference:
    return replace(ref, target=identities.get(ref.target, ref.target))


def remap_capture(value: CapturedSurface, identities: dict[str, str]) -> CapturedSurface:
    return replace(value, reference=remap(value.reference, identities))
