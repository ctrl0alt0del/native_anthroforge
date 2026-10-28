"""Pinned numerical subset remains independently auditable."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "native/vendor/blender_bmesh"


def test_all_blender_subset_files_match_provenance():
    manifest = json.loads((ROOT / "sources.json").read_text())
    assert manifest["tag"] == "v5.0.1"
    for relative, record in manifest["files"].items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == record["sha256"]
        assert len(record["source_sha256"]) == 64
        ranges = record.get("omitted", [])
        assert all(0 <= start < end for start, end in ranges)
        assert all(a[1] <= b[0] for a, b in zip(ranges, ranges[1:], strict=False))
