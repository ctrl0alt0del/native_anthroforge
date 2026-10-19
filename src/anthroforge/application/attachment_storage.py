"""Attachment buffers have explicit archive ownership, independent of evaluated results."""

from typing import Any

from anthroforge.native import attachment_fields, paths

from .attachment_assets import AttachmentAsset

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
    field = attachment_fields.Field(values[0], values[1], values[2], values[3], path)
    return AttachmentAsset(tuple(metadata["targets"]), field)


def describe(assets: dict[str, AttachmentAsset]) -> dict[str, Any]:
    return {
        key: dict(targets=asset.targets, closed=asset.field.path.closed)
        for key, asset in assets.items()
    }
