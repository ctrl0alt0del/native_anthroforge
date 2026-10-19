"""Pin the addon's numerical routing closure; never import Blender or its Python package."""

import hashlib
import json
import sys
from pathlib import Path

HEADERS = (
    "af_roadmap_preparation.hpp",
    "af_fiber_planner43.hpp",
    "af_fiber_contact3.hpp",
    "af_fiber_v3_session.hpp",
    "af_fiber_v3_batch.hpp",
    "af_fiber_v3_operations.hpp",
    "af_fiber_v3_coordinator.hpp",
    "af_fiber_v3_native_sqp.hpp",
)


def capture(source: Path, destination: Path, name: str, first=0, last=None):
    data = (source / name).read_bytes()
    text = data.decode("utf-8").splitlines(keepends=True)
    output = "".join(text[first:last]).encode("utf-8")
    target = name if name.endswith("hpp") else "collision_reference.hpp"
    (destination / target).write_bytes(output)
    return dict(
        source=name,
        source_sha256=hashlib.sha256(data).hexdigest(),
        lines=[first + 1, last or len(text)],
        file=target,
        sha256=hashlib.sha256(output).hexdigest(),
    )


def main():
    source = Path(sys.argv[1]) / "native/fiber_ccd"
    destination = Path(__file__).resolve().parents[1] / "native/migration/routing"
    destination.mkdir(parents=True, exist_ok=True)
    records = [capture(source, destination, "af_fiber_ccd.cpp", 26, 550)]
    records.extend(capture(source, destination, name) for name in HEADERS)
    (destination / "sources.json").write_text(
        json.dumps(records, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
