"""Rebuild the unmodified frame subset from the pinned Blender curve.cc file."""

import hashlib
import json
import sys
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1] / "native/vendor/blender_bevel"
    record = json.loads((root / "sources.json").read_text())
    source = Path(sys.argv[1]).read_bytes()
    assert hashlib.sha256(source).hexdigest() == record["source_sha256"]
    pieces = [source[row["start"] : row["end"]] for row in record["functions"]]
    for piece, row in zip(pieces, record["functions"], strict=True):
        assert hashlib.sha256(piece).hexdigest() == row["sha256"]
    content = record["prefix"].encode() + b"\n\n".join(pieces) + b"\n"
    assert hashlib.sha256(content).hexdigest() == record["sha256"]
    (root / record["file"]).write_bytes(content)


if __name__ == "__main__":
    main()
