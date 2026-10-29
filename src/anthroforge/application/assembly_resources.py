"""Selective resource loading and identity-safe transfer across independent documents."""

import zipfile
from dataclasses import replace
from typing import Any
from uuid import uuid4

from anthroforge.core import graph_records

from . import attachment_storage, object_codec, resource_storage
from .resources import Resources, references

METADATA = dict(
    meshes="assets", paths="paths", images="images", attachments="attachments", bindings="bindings"
)


def required(source: Any, selection: Any) -> dict[str, set[str]]:
    entities = [v for k, v in selection.records.items() if k in source.document.index.entities]
    objects = [v for k, v in selection.records.items() if k in source.document.registry.authored]
    found = references(entities, objects)
    complete_metadata(source.metadata, found)
    return found


def complete_metadata(data: Any, found: dict[str, set[str]]) -> None:
    visited: set[tuple[str, str]] = set()
    while pending := {(kind, key) for kind, keys in found.items() for key in keys} - visited:
        visited |= pending
        for kind, key in pending:
            if kind == "paths":
                item = object_codec.decode(data["paths"][key]["authored"])
                nested = references((), (item,))
                for group, values in nested.items():
                    found[group] |= values
            if kind == "attachments":
                targets = data["attachments"][key]["targets"]
                found["meshes"].update(t["material_asset"] for t in targets)


def load(source: Any, selection: Any, engine: Any, cancel: Any, cache: Any = None) -> Resources:
    from .assembly_source import cancelled

    found, result, cache = required(source, selection), Resources(), cache or Resources()
    with zipfile.ZipFile(source.path) as archive:
        for kind, keys in found.items():
            for key in keys:
                cancelled(cancel)
                stored = getattr(cache, kind)
                if key not in stored:
                    stored[key] = read_one(archive, source.metadata, engine, kind, key)
                getattr(result, kind)[key] = stored[key]
    return result


def read_one(archive: Any, data: Any, engine: Any, kind: str, key: str) -> Any:
    if kind == "evidence":
        return archive.read("evidence/" + key)
    if kind == "bindings":
        return resource_storage.read_bindings(archive, (key,))[key]
    readers = dict(
        meshes=resource_storage.read_mesh,
        paths=resource_storage.read_path,
        images=resource_storage.read_image,
        attachments=attachment_storage.read,
    )
    return readers[kind](archive, key, data[METADATA[kind]][key], engine)


def transfer(resources: Resources, identities: dict[str, str]) -> tuple[Resources, dict[str, str]]:
    keys = {key for kind in METADATA for key in getattr(resources, kind)}
    mapping = {key: str(uuid4()) for key in keys}
    copied = Resources()
    for kind in METADATA:
        for key, value in getattr(resources, kind).items():
            getattr(copied, kind)[mapping[key]] = remapped(value, kind, identities, mapping)
    return copied, mapping


def remapped(value: Any, kind: str, ids: dict[str, str], assets: dict[str, str]) -> Any:
    if kind == "paths":
        return replace(value, authored=graph_records.rewritten(value.authored, ids, assets))
    if kind == "attachments":
        return replace(value, targets=graph_records.rewritten(value.targets, ids, assets))
    return value


def restore_legacy_inputs(preparation: Any) -> None:
    attachment_storage.restore_frame_hints(
        preparation.source.document, preparation.loaded, preparation.engine
    )
    for key, value in preparation.loaded.attachments.items():
        preparation.resources.attachments[preparation.assets[key]] = remapped(
            value, "attachments", preparation.ids, preparation.assets
        )
