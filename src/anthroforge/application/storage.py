"""Portable revision packages and cooperative single-writer file ownership."""

import io
import json
import os
import tempfile
import zipfile
from dataclasses import asdict
from pathlib import Path
from typing import Any
from uuid import UUID

import numpy as np

from anthroforge.core.document import Document
from anthroforge.core.entities import SCP, Attachment, Workspace
from anthroforge.native.mesh import GeometryEngine
from anthroforge.native.topology import restore

from .assets import Asset
from .construction_codec import control, entity_construction
from .geometry_ownership import assets_used

FORMAT = "anthroforge-project"
VERSION = 2
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
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(self.stream.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            fcntl.flock(self.stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)  # type: ignore[attr-defined]

    def close(self) -> None:
        self.stream.close()


def manifest(document: Document, assets: dict[str, Asset]) -> dict[str, Any]:
    state = asdict(document)
    state["id"] = str(document.id)
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
    return Workspace(**data)


def decode_document(data: dict[str, Any]) -> Document:
    data = dict(data)
    if data.pop("metres_per_unit") != 1.0:
        raise ValueError("Project geometry must use canonical metres.")
    data["id"] = UUID(data["id"])
    data["entities"] = tuple(decode_entity(item) for item in data["entities"])
    data["workspaces"] = tuple(decode_workspace(item) for item in data["workspaces"])
    data["controls"] = tuple(control(item) for item in data.get("controls", ()))
    if not data["workspaces"]:
        raise ValueError("Project has no workspace.")
    return Document(**data)


def read_asset(
    archive: zipfile.ZipFile, key: str, source: dict[str, Any], engine: GeometryEngine, version: int
) -> Asset:
    arrays = [
        read_array(archive, f"assets/{key}/{label}.npy")
        for label in (BUFFERS if version == 2 else BUFFERS[:3])
    ]
    mesh = restore(engine, arrays) if version == 2 else engine.create_mesh(*arrays)
    return Asset(mesh, source["source"], source["digest"], source["units"], source["y_up"])


def read_package(path: Path, engine: GeometryEngine) -> tuple[Document, dict[str, Asset]]:
    with zipfile.ZipFile(path) as archive:
        data = json.loads(archive.read("manifest.json"))
        if data.get("format") != FORMAT or data.get("version") not in (1, VERSION):
            raise ValueError("Unsupported AnthroForge project format/version.")
        document = decode_document(data["document"])
        assets = {
            key: read_asset(archive, key, source, engine, data["version"])
            for key, source in data["assets"].items()
        }
        if assets_used(document) - assets.keys():
            raise ValueError("Project is missing a required mesh asset.")
        return document, assets
