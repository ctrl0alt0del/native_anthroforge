"""Typed resource ownership; snapshots retain allocations independently of live catalogues."""

from collections.abc import Iterable
from dataclasses import dataclass, field

from anthroforge.core.construction import Curve
from anthroforge.core.document import Document
from anthroforge.core.entities import SCP
from anthroforge.core.fibers import Fiber
from anthroforge.core.object_registry import Authored
from anthroforge.core.points import Anchor
from anthroforge.core.reference_images import ReferenceImage
from anthroforge.core.surfaces import Surface
from anthroforge.core.tissues import TissueVCP
from anthroforge.native.binding_batches import BindingBatch

from .assets import Asset
from .attachment_assets import AttachmentAsset
from .image_assets import ImageAsset
from .path_assets import PathAsset
from .reconstruction_resources import retain as retain_reconstruction
from .skin_assets import SkinAsset
from .skin_assets import references as skin_references
from .tissue_material_resources import retain as retain_materials


@dataclass
class Resources:
    meshes: dict[str, Asset] = field(default_factory=dict)
    paths: dict[str, PathAsset] = field(default_factory=dict)
    images: dict[str, ImageAsset] = field(default_factory=dict)
    attachments: dict[str, AttachmentAsset] = field(default_factory=dict)
    bindings: dict[str, BindingBatch] = field(default_factory=dict)
    skin: dict[str, SkinAsset] = field(default_factory=dict)
    evidence: dict[str, bytes] = field(default_factory=dict)

    def snapshot(self) -> "Resources":
        return Resources(
            dict(self.meshes),
            dict(self.paths),
            dict(self.images),
            dict(self.attachments),
            dict(self.bindings),
            dict(self.skin),
            dict(self.evidence),
        )

    def selected(self, document: Document) -> "Resources":
        self.require(document)
        keys = referenced(document)
        return Resources(
            **{
                kind: {key: getattr(self, kind)[key] for key in required}
                for kind, required in keys.items()
            }
        )

    def require(self, document: Document) -> None:
        for kind, keys in referenced(document).items():
            missing = keys - getattr(self, kind).keys()
            if missing:
                raise ValueError(
                    f"Project is missing required {kind}: {', '.join(sorted(missing))}"
                )


def referenced(document: Document) -> dict[str, set[str]]:
    opening = tuple(item for context in document.shortcut_edits for item in context.opening)
    result = references((*document.entities, *opening), document.objects)
    result["meshes"].update(shortcut_materials(document))
    result["meshes"].update(
        key
        for r in document.external_references
        for key in (r.surface_asset, r.surface_base)
        if key
    )
    meshes, buffers = skin_references(document.skin)
    result["meshes"].update(meshes)
    result["skin"] = buffers
    retain_reconstruction(document, result)
    return result


def shortcut_materials(document: Document) -> set[str]:
    bindings = {
        b.attachment.material_asset
        for context in document.shortcut_edits
        for b in context.bindings
        if b.attachment.material_asset
    }
    return bindings | {
        c.anchor.material_asset
        for c in document.shortcut_edits
        if c.anchor and c.anchor.material_asset
    }


def references(entities: Iterable[SCP], objects: Iterable[Authored]) -> dict[str, set[str]]:
    entities, objects = tuple(entities), tuple(objects)
    meshes = mesh_references(entities, objects)
    paths = {o.result.asset for o in objects if isinstance(o, Curve)}
    paths.update(o.edit.baseline for o in objects if isinstance(o, Fiber) and o.edit)
    paths.update(tissue_bases(objects, "CURVE"))
    images = {o.source for o in objects if isinstance(o, ReferenceImage)}
    attachments = {o.attachment_asset for o in objects if isinstance(o, Fiber)}
    groups = dict(meshes=meshes, paths=paths, images=images, attachments=attachments)
    groups["bindings"] = {
        r.binding_asset for o in objects if isinstance(o, TissueVCP) for r in o.constraints
    }
    retain_materials(objects, groups)
    return {key: values - {""} for key, values in groups.items()}


def mesh_references(entities: Iterable[SCP], objects: Iterable[Authored]) -> set[str]:
    from anthroforge.core.results import geometry_asset

    meshes = {geometry_asset(e) for e in entities}
    meshes.update(e.primitive.source for e in entities if e.primitive)
    meshes.update(e.attachment.material_asset for e in entities)
    meshes.update(
        e.pose_receipt.effective.material_asset
        for e in entities
        if e.pose_receipt and e.pose_receipt.effective
    )
    meshes.update(o.result.asset for o in objects if isinstance(o, Surface))
    return meshes | tissue_meshes(objects) | binding_meshes(objects)


def tissue_meshes(objects: Iterable[Authored]) -> set[str]:
    rows = tuple(objects)
    return tissue_bases(rows, "SURFACE") | {
        result.asset
        for item in rows
        if isinstance(item, TissueVCP)
        for result in (
            item.result,
            item.rest_result,
            item.intrinsic_result,
            item.final_result,
        )
    }


def binding_meshes(objects: Iterable[Authored]) -> set[str]:
    rows = tuple(objects)
    anchors = {o.binding.material_asset for o in rows if isinstance(o, Anchor)}
    fields = {s.material_asset for o in rows if isinstance(o, Fiber) for s in o.supports}
    pins = {b.material_asset for o in rows if isinstance(o, Fiber) for b in o.bindings}
    regions = {r.material_asset for o in rows if isinstance(o, TissueVCP) for r in o.constraints}
    return anchors | fields | pins | regions


def tissue_bases(objects: Iterable[Authored], kind: str) -> set[str]:
    return {
        item.base_result.asset
        for item in objects
        if isinstance(item, TissueVCP) and item.base_state.kind == kind
    }
