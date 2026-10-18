"""Typed resource ownership; snapshots retain allocations independently of live catalogues."""

from collections.abc import Iterable
from dataclasses import dataclass, field

from anthroforge.core.construction import Curve
from anthroforge.core.document import Document
from anthroforge.core.entities import SCP
from anthroforge.core.object_registry import Construction
from anthroforge.core.reference_images import ReferenceImage
from anthroforge.core.surfaces import Surface

from .assets import Asset
from .image_assets import ImageAsset
from .path_assets import PathAsset


@dataclass
class Resources:
    meshes: dict[str, Asset] = field(default_factory=dict)
    paths: dict[str, PathAsset] = field(default_factory=dict)
    images: dict[str, ImageAsset] = field(default_factory=dict)

    def snapshot(self) -> "Resources":
        return Resources(dict(self.meshes), dict(self.paths), dict(self.images))

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
    return references(document.entities, document.objects)


def references(entities: Iterable[SCP], objects: Iterable[Construction]) -> dict[str, set[str]]:
    from anthroforge.core.results import geometry_asset

    entities, objects = tuple(entities), tuple(objects)
    meshes = {geometry_asset(e) for e in entities}
    meshes.update(e.primitive.source for e in entities if e.primitive)
    meshes.update(o.result.asset for o in objects if isinstance(o, Surface))
    paths = {o.result.asset for o in objects if isinstance(o, Curve)}
    images = {o.source for o in objects if isinstance(o, ReferenceImage)}
    return {
        key: values - {""}
        for key, values in dict(meshes=meshes, paths=paths, images=images).items()
    }
