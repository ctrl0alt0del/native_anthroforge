"""Attachment buffers have explicit archive ownership, independent of evaluated results."""

from dataclasses import asdict, replace
from typing import Any

from anthroforge.core.entities import IDENTITY
from anthroforge.native import attachment_fields, paths

from .attachment_assets import AttachmentAsset
from .surface_reference_codec import capture

BUFFERS = ("owners", "weights", "bindings", "records")


def restore_frame_hints(document: Any, resources: Any, engine: Any) -> None:
    from anthroforge.core.fibers import Fiber

    from .object_frames import Frames

    frames = Frames(engine, document)
    for item in document.objects:
        if not isinstance(item, Fiber) or item.attachment_asset not in resources.attachments:
            continue
        asset = resources.attachments[item.attachment_asset]
        if asset.field.frames or asset.field.frame_hints:
            continue
        hints = tuple(surface_hint(engine, document, resources, t) for t in asset.targets)
        field = replace(asset.field, world=frames.world(item.id), frame_hints=hints)
        resources.attachments[item.attachment_asset] = replace(asset, field=field)


def surface_hint(engine: Any, document: Any, resources: Any, target: Any) -> Any:
    from . import surface_providers

    try:
        return surface_providers.get(engine, document, resources.meshes, target.reference).frame
    except ValueError:
        # A missing prerequisite must not prevent opening accepted geometry. Evaluation
        # still reports that failure; this zero hint does not replace any required input.
        return (0.0,) * 16


def write(archive: Any, assets: dict[str, AttachmentAsset]) -> None:
    from .resource_storage import write_array

    for key, asset in assets.items():
        for name in BUFFERS:
            write_array(archive, f"attachments/{key}/{name}.npy", getattr(asset.field, name))
        write_array(archive, f"attachments/{key}/samples.npy", asset.field.path.array())
        write_array(archive, f"attachments/{key}/parameters.npy", asset.field.path.array(1))


def read(archive: Any, key: str, metadata: Any, engine: Any) -> AttachmentAsset:
    from .resource_storage import read_array

    values = {name: read_array(archive, f"attachments/{key}/{name}.npy") for name in BUFFERS}
    samples = read_array(archive, f"attachments/{key}/samples.npy")
    parameters = read_array(archive, f"attachments/{key}/parameters.npy")
    path = paths.restore(engine, samples, parameters, metadata["closed"])
    field = attachment_fields.Field(
        **values,
        path=path,
        world=tuple(metadata.get("world", IDENTITY)),
        frames=tuple(tuple(f) for f in metadata.get("frames", ())),
        frame_hints=tuple(tuple(f) for f in metadata.get("frame_hints", ())),
    )
    return AttachmentAsset(tuple(capture(row) for row in metadata["targets"]), field)


def describe(assets: dict[str, AttachmentAsset]) -> dict[str, Any]:
    return {
        key: dict(
            targets=[asdict(s) for s in asset.targets],
            closed=asset.field.path.closed,
            world=asset.field.world,
            frames=asset.field.frames,
            frame_hints=asset.field.frame_hints,
        )
        for key, asset in assets.items()
    }
