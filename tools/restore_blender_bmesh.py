"""Reproduce the pinned BMesh subset from a local, verified Blender source tree."""

import argparse
import hashlib
import json
from pathlib import Path

DESTINATION = Path(__file__).resolve().parents[1] / "native/vendor/blender_bmesh"


def verified(path: Path, digest: str) -> bytes:
    content = path.read_bytes()
    if hashlib.sha256(content).hexdigest() != digest:
        raise ValueError(f"Pinned Blender source differs: {path}")
    return content


def restore(source: Path, relative: str, record: dict) -> None:
    content = verified(source / relative, record["source_sha256"])
    for start, end in reversed(record.get("omitted", [])):
        content = content[:start] + b"\n" * content[start:end].count(b"\n") + content[end:]
    if hashlib.sha256(content).hexdigest() != record["sha256"]:
        raise ValueError(f"Subset reconstruction differs: {relative}")
    output = DESTINATION / relative
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(content)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Extracted Blender v5.0.1 source directory")
    source = parser.parse_args().source
    manifest = json.loads((DESTINATION / "sources.json").read_text())
    for relative, record in manifest["files"].items():
        restore(source, relative, record)
    print(f"Verified and restored {len(manifest['files'])} pinned source files.")


if __name__ == "__main__":
    main()
