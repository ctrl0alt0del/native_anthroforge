"""Accepted inspection surfaces, including document skin, without authored proxy objects."""

from dataclasses import dataclass
from typing import Any

from anthroforge.core.entities import IDENTITY, SCP
from anthroforge.core.mirroring import source
from anthroforge.core.results import geometry_asset
from anthroforge.core.surfaces import Surface as ConstructionSurface
from anthroforge.core.tissues import TissueVCP
from anthroforge.native import scene
from anthroforge.native.construction import matrix

from . import tissue_inspection_stages as stages
from .object_frames import Frames


@dataclass(frozen=True)
class Surface:
    target: str
    stage: str
    asset: str
    frame: tuple[float, ...]
    revision: int
    name: str
    kind: str

    def mesh(self, context: Any) -> Any:
        resource = context.resources.meshes.get(self.asset)
        if resource is None:
            raise ValueError("This stage has no accepted surface. Evaluate it first.")
        return resource.mesh


def skin_id(document: Any) -> str:
    return "skin:" + str(document.id)


def get(context: Any, target: str, stage: str = "final") -> Surface:
    if target in ("skin", skin_id(context.document)):
        return skin(context.document, stage)
    item = context.document.object(source(target))
    if isinstance(item, TissueVCP):
        return tissue(context, target, item, stage)
    if stage not in ("final", "geometry"):
        raise ValueError("This object provides its evaluated geometry only.")
    if not isinstance(item, (SCP, ConstructionSurface)):
        raise ValueError("Select an object with an accepted surface.")
    return geometry(context, target, item)


def tissue(context: Any, target: str, item: Any, stage: str) -> Surface:
    value = stages.result(item, stage)
    frame = stages.instance_frame(context, target, stage)
    return Surface(target, stage, value.asset, tuple(frame), value.revision, item.name, "TISSUE")


def geometry(context: Any, target: str, item: Any) -> Surface:
    frame = object_frame(context, target, item)
    return Surface(
        target,
        "geometry",
        geometry_asset(item),
        frame,
        item.result.revision,
        item.name,
        type(item).__name__,
    )


def eligibility(context: Any, target: str, stage: str = "final") -> Any:
    from .operation_status import assess

    return assess(lambda: get(context, target, stage).mesh(context))


def skin(document: Any, stage: str) -> Surface:
    if stage not in ("envelope", "topology", "final"):
        raise ValueError("Choose envelope, topology or final skin.")
    result = getattr(document.skin, stage)
    return Surface(
        skin_id(document), stage, result.asset, IDENTITY, result.revision, "Skin", "SKIN"
    )


def object_frame(context: Any, target: str, item: Any) -> tuple[float, ...]:
    frame = Frames(context.engine, context.document).world(item.id)
    frame = scene.geometry_matrix(
        context.engine, frame, getattr(item, "geometry_offset", (0, 0, 0))
    )
    if target != item.id:
        instance = context.document.mirrors.instances[target]
        frame = matrix(context.engine, context.document.mirrors.plane(instance).frame, frame)
    return tuple(frame)


def targets(document: Any) -> tuple[str, ...]:
    originals = tuple(
        i.id
        for i in document.registry.records.values()
        if isinstance(i, (SCP, ConstructionSurface, TissueVCP)) and geometry_asset(i)
    )
    mirrors = tuple(k for k, v in document.mirrors.instances.items() if v.source in originals)
    return originals + mirrors
