"""Portable revision packages and cooperative single-writer file ownership."""

import json
import os
import sys
import tempfile
import zipfile
from dataclasses import asdict, fields
from pathlib import Path
from typing import Any
from uuid import UUID

from anthroforge.core.document import Document
from anthroforge.core.entities import SCP, Attachment, AttachmentReceipt, Workspace
from anthroforge.core.junctions import decode as decode_junction
from anthroforge.native.mesh import GeometryEngine

from . import (
    assembly_codec,
    attachment_storage,
    object_codec,
    resource_storage,
    shortcut_codec,
    skin_codec,
)
from .construction_codec import control, entity_construction
from .mirror_codec import fields as mirror_fields
from .resources import Resources

FORMAT = "anthroforge-project"
VERSION = 8
READ_VERSIONS = (4, 5, 6, 7, 8)
STATE_RECORDS = (
    "entities",
    "controls",
    "workspaces",
    "junctions",
    "shortcuts",
    "driving_shortcuts",
    "formula_results",
    "shortcut_edits",
    "mirror_rules",
    "shared_mirror_targets",
    "imports",
    "external_references",
)


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


def manifest(document: Document, resources: Resources) -> dict[str, Any]:
    state = document_state(document)
    return {
        "format": FORMAT,
        "version": VERSION,
        "document": state,
        **resource_storage.describe(resources.selected(document)),
    }


def document_state(document: Document) -> dict[str, Any]:
    from .mirror_codec import snapshot

    state = {
        f.name: getattr(document, f.name) for f in fields(document) if not f.name.startswith("_")
    }
    state["id"] = str(document.id)
    for name in STATE_RECORDS:
        state[name] = [asdict(value) for value in state[name]]
    state["objects"] = [object_codec.encode(value) for value in document.objects]
    state["skin"] = asdict(document.skin)
    state["mirror_accepted"] = snapshot(document)
    return state


def write_package(
    path: Path, document: Document, resources: Resources, cancel: Any = None, recovery: Any = None
) -> None:
    from .cancellable_stream import CancellableStream

    resources = resources.selected(document)
    data = manifest(document, resources)
    with path.open("w+b") as stream:
        with zipfile.ZipFile(CancellableStream(stream, cancel), "w", allowZip64=True) as archive:
            archive.writestr("manifest.json", json.dumps(data, indent=2, allow_nan=False))
            if recovery is not None:
                archive.writestr("recovery.json", json.dumps(recovery, allow_nan=False))
            resource_storage.write(archive, resources)


def atomic_save(
    path: Path, document: Document, resources: Resources, cancel: Any = None, recovery: Any = None
) -> None:
    descriptor, temporary = tempfile.mkstemp(prefix=".anthroforge-", suffix=".tmp", dir=path.parent)
    os.close(descriptor)
    try:
        commit_package(path, Path(temporary), document, resources, cancel, recovery)
    finally:
        Path(temporary).unlink(missing_ok=True)


def commit_package(
    path: Path,
    temporary: Path,
    document: Document,
    resources: Resources,
    cancel: Any,
    recovery: Any,
) -> None:
    write_package(temporary, document, resources, cancel, recovery)
    if cancel is not None and cancel.is_set():
        raise ValueError("Project save cancelled.")
    with temporary.open("r+b") as stream:
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def decode_entity(data: dict[str, Any]) -> SCP:
    data = entity_construction(data)
    attachment = dict(data.pop("attachment"))
    attachment["binding"] = tuple(attachment.get("binding", ()))
    data["matrix"] = tuple(data["matrix"])
    data["geometry_offset"] = tuple(data["geometry_offset"])
    data["capture_parent_matrix"] = tuple(data.get("capture_parent_matrix", ()))
    data["capture_parent_offset"] = tuple(data.get("capture_parent_offset", (0.0, 0.0, 0.0)))
    data["pose_receipt"] = decode_pose_receipt(data.get("pose_receipt"))
    return SCP(**data, attachment=Attachment(**attachment))


def decode_pose_receipt(value: Any) -> AttachmentReceipt | None:
    if value is None:
        return None
    data = dict(value)
    data["parent_reflection"] = tuple(data.get("parent_reflection", ()))
    for key in ("parent_matrix", "parent_offset", "child_matrix", "child_offset"):
        data[key] = tuple(data[key])
    settings = dict(data["settings"])
    settings["binding"] = tuple(settings["binding"])
    if data.get("effective") is not None:
        data["effective"] = decoded_attachment(data["effective"])
    return AttachmentReceipt(**{**data, "settings": Attachment(**settings)})


def decoded_attachment(value: dict[str, Any]) -> Attachment:
    return Attachment(**dict(value, binding=tuple(value.get("binding", ()))))


def decode_workspace(data: dict[str, Any]) -> Workspace:
    from .workspace_policy import settings

    return Workspace(**settings(data))


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
    data["junctions"] = tuple(decode_junction(item) for item in data.get("junctions", ()))
    return restored_document(data)


def restored_document(data: dict[str, Any]) -> Document:
    if not data["workspaces"]:
        raise ValueError("Project has no workspace.")
    mirrors = mirror_fields(data)
    data.pop("mirror_accepted", None)
    data["skin"] = skin_codec.decode(data.get("skin"))
    assembly = assembly_codec.decode(data)
    return Document(**(data | shortcut_codec.document_fields(data) | mirrors | assembly))


def read_package(path: Path, engine: GeometryEngine) -> tuple[Document, Resources]:
    with zipfile.ZipFile(path) as archive:
        data = json.loads(archive.read("manifest.json"))
        if data.get("format") != FORMAT or data.get("version") not in READ_VERSIONS:
            raise ValueError("Unsupported AnthroForge project format/version.")
        document = decode_document(data["document"])
        resources = resource_storage.read(archive, data, engine)
        resources.require(document)
        attachment_storage.restore_frame_hints(document, resources, engine)
        return document, resources
