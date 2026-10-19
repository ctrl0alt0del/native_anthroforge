"""Capture maintained addon creation defaults without changing source projects."""

import hashlib
import importlib
import json
import sys
from dataclasses import asdict
from pathlib import Path


def capture(addon, output):
    sys.path.insert(0, str(addon))
    module = importlib.import_module("core.vcp.soft_tissue_presets")
    source = addon / "core/vcp/soft_tissue_presets.py"
    names = ("CLOSED_BULK", "RIM", "LAYER", "POUCH", "CUSTOM")
    data = dict(
        source=str(source),
        sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        presets={key: asdict(module.preset_values(key)) for key in names},
    )
    output.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    capture(*(Path(value) for value in sys.argv[sys.argv.index("--") + 1 :]))
