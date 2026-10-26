"""Retained Blender frame implementation is auditable independently of geometry fixtures."""

import hashlib
import json
from pathlib import Path


def test_bevel_frame_source_matches_manifest():
    root = Path(__file__).resolve().parents[1] / "native/vendor/blender_bevel"
    record = json.loads((root / "sources.json").read_text())
    content = (root / record["file"]).read_bytes()
    assert hashlib.sha256(content).hexdigest() == record["sha256"]
    offset = len(record["prefix"].encode())
    for row in record["functions"]:
        size = row["end"] - row["start"]
        assert hashlib.sha256(content[offset : offset + size]).hexdigest() == row["sha256"]
        offset += size + 2
