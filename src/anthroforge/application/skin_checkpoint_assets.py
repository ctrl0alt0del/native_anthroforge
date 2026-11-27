"""Immutable checkpoint file bundles with portable paths and validated byte checksums."""

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

import numpy as np

from anthroforge.core.skin_checkpoints import Checkpoint

from . import skin_assets


@dataclass(frozen=True)
class Bundle:
    checkpoint: Checkpoint
    asset: skin_assets.SkinAsset


def relative_name(name: str) -> str:
    path = PurePosixPath(name)
    if (
        path.is_absolute()
        or not path.parts
        or any(p in ("..", ".") or ":" in p or "\\" in p for p in path.parts)
    ):
        raise ValueError("Checkpoint file path must stay inside its bundle.")
    return str(path)


def create(files: dict[str, bytes], state: dict[str, Any]) -> skin_assets.SkinAsset:
    arrays, manifest = {}, {}
    for index, (name, data) in enumerate(sorted(files.items())):
        key = f"file_{index}"
        manifest[relative_name(name)] = dict(array=key, checksum=hashlib.sha256(data).hexdigest())
        arrays[key] = np.frombuffer(data, dtype=np.uint8)
    return skin_assets.create(arrays, dict(kind="builder_checkpoint", files=manifest, state=state))


def validate(asset: skin_assets.SkinAsset) -> dict[str, Any]:
    info = json.loads(asset.metadata)
    if info.get("kind") != "builder_checkpoint" or not info.get("files"):
        raise ValueError("Missing skin construction checkpoint files.")
    for name, row in info["files"].items():
        relative_name(name)
        array = asset.arrays[row["array"]]
        if array.dtype != np.uint8 or array.ndim != 1:
            raise ValueError("Invalid checkpoint byte buffer.")
        if hashlib.sha256(array).hexdigest() != row["checksum"]:
            raise ValueError("Skin checkpoint file checksum mismatch.")
    return dict(info["state"])


def restore(asset: skin_assets.SkinAsset, folder: Path) -> dict[str, Any]:
    state = validate(asset)
    folder.mkdir(parents=True, exist_ok=False)
    info = json.loads(asset.metadata)
    for name, row in info["files"].items():
        target = folder / relative_name(name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(asset.arrays[row["array"]].tobytes())
    return state


def retained(skin: Any, bundles: tuple[Bundle, ...]) -> Any:
    from dataclasses import replace

    builders = {b.checkpoint.builder for b in bundles}
    records = tuple(r for r in skin.checkpoints if r.builder not in builders)
    return replace(skin, checkpoints=(*records, *(b.checkpoint for b in bundles)))
