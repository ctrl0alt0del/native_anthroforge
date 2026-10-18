"""Immutable embedded image data decoded without Qt and with EXIF applied once."""

import io
from dataclasses import dataclass
from hashlib import sha256
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PIL import Image


@dataclass(frozen=True, eq=False)
class ImageAsset:
    encoded: bytes
    rgba: bytes
    width: int
    height: int
    digest: str
    format: str


def decode(encoded: bytes) -> ImageAsset:
    from PIL import Image, ImageOps

    with Image.open(io.BytesIO(encoded)) as source:
        if source.format not in ("PNG", "JPEG"):
            raise ValueError("Reference images support PNG and JPEG only.")
        source.load()
        normalized = ImageOps.exif_transpose(source).convert("RGBA")
        return decoded_asset(encoded, normalized, source.format)


def decoded_asset(encoded: bytes, normalized: "Image.Image", format: str) -> ImageAsset:
    return ImageAsset(
        encoded,
        normalized.tobytes(),
        normalized.width,
        normalized.height,
        sha256(encoded).hexdigest(),
        format,
    )
