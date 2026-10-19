"""Pin only the addon's numerical tissue closure, with byte-exact source provenance."""

import hashlib
import json
import sys
from pathlib import Path

BLOCKS = (
    ("af_muscle_numeric.hpp", "struct AfMuscleInput", "static Vec af_muscle_lerp"),
    (
        "af_muscle_numeric.hpp",
        "static Vec af_muscle_unit",
        "static std::vector<double> af_muscle_spans",
    ),
    ("af_muscle_numeric.hpp", "static Vec af_muscle_centroid", "static void af_muscle_compute"),
    (
        "af_muscle_envelope_profile.hpp",
        "static Vec af_env_unit",
        "AF_EXPORT int af_muscle_envelope_version",
    ),
)


def capture(source, destination, index, block):
    name, start, end = block
    data = (source / name).read_bytes()
    first, last = data.index(start.encode()), data.index(end.encode())
    output = data[first:last]
    filename = f"kernel_{index}.hpp"
    (destination / filename).write_bytes(output)
    return dict(
        source=name,
        source_sha256=hashlib.sha256(data).hexdigest(),
        bytes=[first, last],
        file=filename,
        sha256=hashlib.sha256(output).hexdigest(),
    )


def main():
    source = Path(sys.argv[1]) / "native/fiber_ccd"
    destination = Path(__file__).resolve().parents[1] / "native/migration/tissue"
    destination.mkdir(parents=True, exist_ok=True)
    records = [capture(source, destination, i, block) for i, block in enumerate(BLOCKS)]
    (destination / "sources.json").write_text(
        json.dumps(records, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
