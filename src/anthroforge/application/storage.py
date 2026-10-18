"""Portable revision packages and cooperative single-writer file ownership."""

import io
import json
import os
import sys
import tempfile
import zipfile
from dataclasses import asdict, fields
from pathlib import Path
from typing import Any
from uuid import UUID

import numpy as np

from anthroforge.core.document import Document
from anthroforge.core.entities import SCP, Attachment, Workspace
from anthroforge.core.inspection_views import decode_bookmark, decode_measurement
from anthroforge.native.mesh import GeometryEngine
from anthroforge.native.topology import restore

from . import object_codec
from .assets import Asset
from .construction_codec import control, entity_construction
from .geometry_ownership import assets_used

FORMAT = "anthroforge-project"
VERSION = 3
BUFFERS = ("vertices", "corners", "offsets", "triangles", "polygons")


class FileLock:
    def __init__(self, path: Path) -> None:
        self.path = path.resolve()
        self.stream = Path(str(self.path) + ".lock").open("a+b")
        self.stream.seek(0)
        self.stream.write(b"0")
        self.stream.flush()
        self.stream.seek(0)
        try:
            self._acquire()
        except OSError as error:
            self.stream.close()
            raise ValueError(
                "This project is already open for writing in another session."
            ) from error

    def _acquire(self) -> None:
        if sys.platform == "win32":
            import msvcrt

            msvcrt.locking(self.stream.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            fcntl.flock(self.stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

    def close(self) -> None:
        self.stream.close()


def manifest(document: Document, assets: dict[str, Asset]) -> dict[str, Any]:
    state = document_state(document)
    used = assets_used(document)
    sources = {
        key: {
            "source": assets[key].source,
            "digest": assets[key].digest,
            "units": assets[key].units,
            "y_up": assets[key].y_up,
        }
        for key in used
    }
    return {"format": FORMAT, "version": VERSION, "document": state, "assets": sources}


def document_state(document: Document) -> dict[str, Any]:
    state = {
        f.name: getattr(document, f.name) for f in fields(document) if not f.name.startswith("_")
    }
    state["id"] = str(document.id)
    for name in ("entities", "controls", "workspaces"):
        state[name] = [asdict(value) for value in state[name]]
    state["objects"] = [object_codec.encode(value) for value in document.objects]
    return state


def write_array(archive: zipfile.ZipFile, name: str, array: Any) -> None:
    with archive.open(name, "w", force_zip64=True) as stream:
        np.lib.format.write_array(stream, array, allow_pickle=False)  # type: ignore[no-untyped-call]


def write_package(path: Path, document: Document, assets: dict[str, Asset]) -> None:
    data = manifest(document, assets)
    with zipfile.ZipFile(path, "w", allowZip64=True) as archive:
        archive.writestr("manifest.json", json.dumps(data, indent=2, allow_nan=False))
        for key in data["assets"]:
            for kind, label in enumerate(BUFFERS):
                write_array(archive, f"assets/{key}/{label}.npy", assets[key].mesh.array(kind))


def atomic_save(path: Path, document: Document, assets: dict[str, Asset]) -> None:
    descriptor, temporary = tempfile.mkstemp(prefix=".anthroforge-", suffix=".tmp", dir=path.parent)
    os.close(descriptor)
    try:
        write_package(Path(temporary), document, assets)
        with open(temporary, "r+b") as stream:
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def read_array(archive: zipfile.ZipFile, name: str) -> Any:
    with archive.open(name) as stream:
        return np.load(io.BytesIO(stream.read()), allow_pickle=False)


def decode_entity(data: dict[str, Any]) -> SCP:
    data = entity_construction(data)
    attachment = dict(data.pop("attachment"))
    attachment["binding"] = tuple(attachment.get("binding", ()))
    data["matrix"] = tuple(data["matrix"])
    data["geometry_offset"] = tuple(data["geometry_offset"])
    data["capture_parent_matrix"] = tuple(data.get("capture_parent_matrix", ()))
    data["capture_parent_offset"] = tuple(data.get("capture_parent_offset", (0.0, 0.0, 0.0)))
    return SCP(**data, attachment=Attachment(**attachment))


def decode_workspace(data: dict[str, Any]) -> Workspace:
    data = dict(data)
    for key in ("members", "hidden", "unpickable", "camera"):
        data[key] = tuple(data[key])
    for key in ("hidden_categories", "unpickable_categories"):
        data[key] = tuple(data.get(key, ()))
    data["measurements"] = tuple(map(decode_measurement, data.get("measurements", ())))
    data["bookmarks"] = tuple(map(decode_bookmark, data.get("bookmarks", ())))
    return Workspace(**data)


def decode_document(data: dict[str, Any]) -> Document:
    data = dict(data)
    if any(key.startswith("_") for key in data):
        raise ValueError("Project cannot supply derived runtime indexes.")
    if data.pop("metres_per_unit") != 1.0:
        raise ValueError("Project geometry must use canonical metres.")
    data["id"] = UUID(data["id"])
    data["entities"] = tuple(decode_entity(item) for item in data["entities"])
    data["workspaces"] = tuple(decode_workspace(item) for item in data["workspaces"])
    data["controls"] = tuple(control(item) for item in data.get("controls", ()))
    data["objects"] = tuple(object_codec.decode(item) for item in data.get("objects", ()))
    if not data["workspaces"]:
        raise ValueError("Project has no workspace.")
    return Document(**data)


def read_asset(
    archive: zipfile.ZipFile, key: str, source: dict[str, Any], engine: GeometryEngine
) -> Asset:
    arrays = [read_array(archive, f"assets/{key}/{label}.npy") for label in BUFFERS]
    mesh = restore(engine, arrays)
    return Asset(mesh, source["source"], source["digest"], source["units"], source["y_up"])


def read_package(path: Path, engine: GeometryEngine) -> tuple[Document, dict[str, Asset]]:
    with zipfile.ZipFile(path) as archive:
        data = json.loads(archive.read("manifest.json"))
        if data.get("format") != FORMAT or data.get("version") != VERSION:
            raise ValueError("Unsupported AnthroForge project format/version.")
        document = decode_document(data["document"])
        assets = {
            key: read_asset(archive, key, source, engine) for key, source in data["assets"].items()
        }
        if assets_used(document) - assets.keys():
            raise ValueError("Project is missing a required mesh asset.")
        return document, assets
