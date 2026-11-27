"""Content identities for ordered AVBD prefixes, independent of paths and UI revisions."""

import hashlib
import json
import struct
from functools import lru_cache
from pathlib import Path
from typing import Any

PROTOCOL = 3


@lru_cache(maxsize=2048)
def file_digest(path: Path, size: int, modified: int) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def runtime(root: Path) -> str:
    files = list((root / "tools/runtime/skin").glob("*.py"))
    for directory in ("build/avbd-envelope/cuda-native", "build/quality-mesh"):
        files.extend((root / directory).rglob("*.exe"))
        files.extend((root / directory).rglob("*.dll"))
    records = []
    for path in sorted(files):
        stat = path.stat()
        records.append(
            (path.relative_to(root).as_posix(), file_digest(path, stat.st_size, stat.st_mtime_ns))
        )
    return digest(dict(protocol=PROTOCOL, runtime=records))


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def mesh_digests(path: Path) -> list[str]:
    result = []
    with path.open("rb") as stream:
        count = struct.unpack("<i", stream.read(4))[0]
        for _ in range(count):
            header = stream.read(8)
            vertices, faces = struct.unpack("<ii", header)
            data = stream.read(vertices * 24 + faces * 12)
            if len(data) != vertices * 24 + faces * 12:
                raise ValueError("Truncated captured AVBD geometry.")
            result.append(hashlib.sha256(header + data).hexdigest())
    return result


def prefixes(folder: Path, runtime_id: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    recipe = json.loads((folder / "recipe.json").read_text())
    meshes = mesh_digests(folder / "bones.bin")
    current = digest((runtime_id, (folder / "frame.bin").read_bytes().hex()))
    bones, tissues = [], []
    for row in recipe["bones"]:
        current = digest((current, row, meshes[row["mesh_index"]]))
        bones.append(current)
    for row in recipe["muscles"]:
        geometry = [
            mesh_digests(folder / row["assets"] / (name + ".bin")) for name in ("base", "muscle")
        ]
        current = digest((current, row, geometry))
        tissues.append(current)
    return tuple(bones), tuple(tissues)
