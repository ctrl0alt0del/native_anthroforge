"""Instance-aware provider transforms and provenance; no mirrored numerical solve."""

from dataclasses import replace
from typing import Any

from anthroforge.core import anatomical_surfaces
from anthroforge.core.mirroring import MirrorInstance, parse
from anthroforge.core.surface_references import SurfaceReference
from anthroforge.native.construction import matrix


def normalize(document: Any, target: str | SurfaceReference) -> SurfaceReference:
    ref = target if isinstance(target, SurfaceReference) else from_identity(document, target)
    validated = anatomical_surfaces.reference(ref.target, document.registry.records, ref.role)
    if ref.instance:
        identity = MirrorInstance(ref.target, ref.instance).id
        if identity not in document.mirrors.instances:
            raise ValueError("This mirrored surface instance does not exist.")
    return replace(validated, instance=ref.instance)


def from_identity(document: Any, target: str) -> SurfaceReference:
    instance = parse(target)
    if instance:
        ref = anatomical_surfaces.reference(instance.source, document.registry.records)
        return replace(ref, instance=instance.rule)
    return anatomical_surfaces.reference(target, document.registry.records)


def frame(engine: Any, document: Any, ref: SurfaceReference, source: Any) -> Any:
    if not ref.instance:
        return source
    return matrix(engine, document.mirrors.rules[ref.instance].frame, source)


def references(document: Any) -> tuple[SurfaceReference, ...]:
    return tuple(
        SurfaceReference(instance.source, role, instance.rule)
        for instance in document.mirrors.instances.values()
        if instance.source in document.registry.anatomy
        for role in anatomical_surfaces.roles(
            document.object(instance.source), document.registry.records
        )
    )
