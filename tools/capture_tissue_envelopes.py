"""Qualify production two-side composition against pinned independently inflated sides."""

import hashlib
import importlib
import json
import sys
from pathlib import Path


def case(module, rows, index, disabled):
    source = rows[index]
    opposite = next(r for r in rows if r["name"] == source["name"].replace("flipFalse", "flipTrue"))
    first = source["points"] if disabled in ("a", "both") else source["output"]
    second = source["points"] if disabled in ("b", "both") else opposite["output"]
    vertices, faces, origins, sides = module.compose(first, second, source["faces"])
    return record(index, disabled, vertices, faces, origins, sides, first, second)


def record(index, disabled, vertices, faces, origins, sides, first, second):
    return dict(
        source=index,
        disabled=disabled,
        vertices=vertices.tolist(),
        faces=faces.tolist(),
        origins=origins.tolist(),
        sides=sides.tolist(),
        first=first,
        second=second,
    )


def main(addon, fixtures):
    sys.path.insert(0, str(addon))
    module = importlib.import_module("core.vcp.muscle_envelope_native")
    rows = json.loads((fixtures / "branches.json").read_text())["cases"]
    cases = [case(module, rows, i, d) for i in (0, 1, 4, 5) for d in ("", "a", "b", "both")]
    source = addon / "native/fiber_ccd/af_muscle_envelope_compose.hpp"
    data = dict(
        source=str(source.relative_to(addon)),
        sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        cases=cases,
    )
    (fixtures / "envelopes.json").write_text(json.dumps(data, allow_nan=False) + "\n")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
