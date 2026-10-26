"""Checksummed skin buffers in the ordinary project archive."""

import json
from typing import Any

from .skin_assets import SkinAsset, create


def describe(assets: dict[str, SkinAsset]) -> dict[str, Any]:
    return {
        key: {
            "digest": item.digest,
            "arrays": list(item.arrays),
            "metadata": json.loads(item.metadata),
        }
        for key, item in assets.items()
    }


def write(archive: Any, assets: dict[str, SkinAsset]) -> None:
    from .resource_storage import write_array

    for key, asset in assets.items():
        for name, array in asset.arrays.items():
            write_array(archive, f"skin/{key}/{name}.npy", array)


def read(archive: Any, values: dict[str, Any]) -> dict[str, SkinAsset]:
    return {key: read_asset(archive, key, row) for key, row in values.items()}


def read_asset(archive: Any, key: str, row: dict[str, Any]) -> SkinAsset:
    from .resource_storage import read_array

    asset = create(
        {name: read_array(archive, f"skin/{key}/{name}.npy") for name in row["arrays"]},
        row["metadata"],
    )
    if asset.digest != row["digest"]:
        raise ValueError("Skin resource checksum mismatch.")
    return asset
