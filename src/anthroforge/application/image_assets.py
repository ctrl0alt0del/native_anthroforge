"""Immutable embedded image data decoded without Qt and with EXIF applied once."""

import dataclasses
import io
from dataclasses import dataclass
from hashlib import sha256
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PIL import Image

    from anthroforge.native.images import Image as NativeImage
    from anthroforge.native.mesh import GeometryEngine


@dataclass(frozen=True, eq=False)
class ImageAsset:
    encoded: bytes
    rgba: bytes
    width: int
    height: int
    digest: str
    format: str
    texture: "NativeImage | None" = None


def decode(encoded: bytes, engine: "GeometryEngine | None" = None, cancel: int = 0) -> ImageAsset:
    from PIL import Image, ImageOps

    with Image.open(io.BytesIO(encoded)) as source:
        if source.format not in ("PNG", "JPEG"):
            raise ValueError("Reference images support PNG and JPEG only.")
        source.load()
        normalized = ImageOps.exif_transpose(source).convert("RGBA")
        return decoded_asset(encoded, normalized, source.format, engine, cancel)


def decoded_asset(
    encoded: bytes,
    normalized: "Image.Image",
    format: str,
    engine: "GeometryEngine | None",
    cancel: int,
) -> ImageAsset:
    rgba = normalized.tobytes()
    asset = ImageAsset(
        encoded, rgba, normalized.width, normalized.height, sha256(encoded).hexdigest(), format
    )
    return prepare_texture(asset, engine, cancel) if engine else asset


def prepare_texture(asset: ImageAsset, engine: "GeometryEngine", cancel: int) -> ImageAsset:
    from anthroforge.native.images import Image as NativeImage

    texture = NativeImage(engine, asset.rgba, asset.width, asset.height, cancel)
    return dataclasses.replace(asset, texture=texture)
