"""Pinned donor and third-party bytes survive checkout without newline conversion."""

import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1] / "native"


@pytest.mark.parametrize(
    "folder,manifest",
    [
        ("migration/smoothing", "migration/smoothing/sources.json"),
        ("migration/stacking", "migration/stacking/sources.json"),
        ("vendor", "vendor/piqp-sha256.json"),
    ],
)
def test_pinned_numerical_sources_match_provenance(folder, manifest):
    for name, expected in json.loads((ROOT / manifest).read_text()).items():
        assert hashlib.sha256((ROOT / folder / name).read_bytes()).hexdigest() == expected, name
