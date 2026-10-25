"""Attachment buffers have explicit archive ownership, independent of evaluated results."""

from dataclasses import asdict
from typing import Any

from anthroforge.native import attachment_fields, paths
from anthroforge.core.entities import IDENTITY

from .attachment_assets import AttachmentAsset
from .surface_reference_codec import capture

BUFFERS = ("owners", "weights", "bindings", "records")


def write(archive: Any, assets: dict[str, AttachmentAsset]) -> None:
    from .resource_storage import write_array

    for key, asset in assets.items():
        for name in BUFFERS:
            write_array(archive, f"attachments/{key}/{name}.npy", getattr(asset.field, name))
        write_array(archive, f"attachments/{key}/samples.npy", asset.field.path.array())
        write_array(archive, f"attachments/{key}/parameters.npy", asset.field.path.array(1))


def read(archive: Any, key: str, metadata: Any, engine: Any) -> AttachmentAsset:
    from .resource_storage import read_array

    values = [read_array(archive, f"attachments/{key}/{name}.npy") for name in BUFFERS]
    samples = read_array(archive, f"attachments/{key}/samples.npy")
    parameters = read_array(archive, f"attachments/{key}/parameters.npy")
    path = paths.restore(engine, samples, parameters, metadata["closed"])
    field = attachment_fields.Field(*values, path, tuple(metadata.get("world", IDENTITY)),
                                    tuple(tuple(f) for f in metadata.get("frames", ())))
    return AttachmentAsset(tuple(capture(row) for row in metadata["targets"]), field)


def describe(assets: dict[str, AttachmentAsset]) -> dict[str, Any]:
    return {
        key: dict(targets=[asdict(s) for s in asset.targets], closed=asset.field.path.closed,
                  world=asset.field.world, frames=asset.field.frames)
        for key, asset in assets.items()
    }
