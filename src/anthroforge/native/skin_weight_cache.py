"""Disposable, checksummed FAST weights; computation still owns all numerical work."""

import hashlib
import json
import os
import re
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any
from zipfile import ZIP_STORED, BadZipFile, ZipFile

FORMAT = "anthroforge-bbw-v1"
FAILURES = (OSError, ValueError, KeyError, BadZipFile)


def directory() -> Path:
    base = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / ".cache")))
    return base / "AnthroForge" / "deformation" / FORMAT


def key(data: tuple[Any, ...], handles: int) -> str:
    digest = hashlib.sha256(f"{FORMAT}:{handles}".encode())
    for array in data[:3]:
        digest.update(f"{array.dtype}:{array.shape}".encode())
        digest.update(memoryview(array).cast("B"))
    return digest.hexdigest()


def checksum(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def restore(identity: str, folder: str) -> str:
    try:
        with ZipFile(directory() / (identity + ".zip")) as archive:
            restore_archive(archive, Path(folder))
        return "hit"
    except FileNotFoundError:
        return "miss"
    except FAILURES:
        return "unavailable"


def restore_archive(archive: ZipFile, folder: Path) -> None:
    if archive.getinfo("manifest.json").file_size > 4096:
        raise ValueError("Invalid weight cache manifest.")
    info = json.loads(archive.read("manifest.json"))
    name = info["name"]
    if info["format"] != FORMAT or not re.fullmatch(r"bbw_v1_\d+\.bin", name):
        raise ValueError("Invalid weight cache identity.")
    pending = folder / "restore.tmp"
    with archive.open(name) as source, pending.open("wb") as target:
        shutil.copyfileobj(source, target, 1024 * 1024)
    if checksum(pending) != info["sha256"]:
        raise ValueError("Weight cache checksum mismatch.")
    pending.replace(folder / name)


def retain(identity: str, folder: str) -> bool:
    try:
        files = tuple(Path(folder).glob("bbw_v1_*.bin"))
        if len(files) != 1:
            return False
        destination = directory() / (identity + ".zip")
        destination.parent.mkdir(parents=True, exist_ok=True)
        publish(destination, files[0])
        return True
    except FAILURES:
        return False


def publish(destination: Path, weights: Path) -> None:
    with NamedTemporaryFile(dir=destination.parent, suffix=".tmp", delete=False) as stream:
        pending = Path(stream.name)
    try:
        info = dict(format=FORMAT, name=weights.name, sha256=checksum(weights))
        with ZipFile(pending, "w", compression=ZIP_STORED) as archive:
            archive.write(weights, weights.name)
            archive.writestr("manifest.json", json.dumps(info))
        pending.replace(destination)
    finally:
        pending.unlink(missing_ok=True)


def prepare(engine: Any, value: Any, data: Any, settings: Any, folder: str, cancel: int) -> Any:
    import ctypes

    identity = key(data, settings.fast_handles) if settings.method == "FAST" else ""
    status = restore(identity, folder) if identity else "disabled"
    handle = int(engine.library.af_skin_deformation_prepare(ctypes.byref(value), cancel))
    engine.check(not handle)
    if identity and status != "hit":
        retain(identity, folder)
    return handle, status
