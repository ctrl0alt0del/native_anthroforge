"""Compare transition geometry, connectivity and quality against addon captures."""

import json
import sys
from pathlib import Path

import numpy as np

from anthroforge.native import skin_stitch
from anthroforge.native.mesh import GeometryEngine


def evaluate(engine, row):
    plane = [0, 0, 0, 1, 0, 0] if row["symmetric"] else None
    return skin_stitch.build(engine, row["first"], row["second"], 8.0, plane)


def check(engine, row):
    try:
        result = evaluate(engine, row)
    except ValueError as error:
        return dict(native_error=str(error), addon_error=row.get("error"))
    points = result.topology.mesh.array(0)
    faces = result.topology.mesh.array(1).reshape(-1, 4)
    return dict(
        error=float(np.max(np.abs(points - row["points"]))),
        faces_equal=bool(np.array_equal(faces, row["faces"])),
        native=result.diagnostics.tolist(),
        addon=row["diagnostics"],
    )


def main():
    rows = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["cases"]
    results = [check(GeometryEngine(), row) for row in rows]
    Path(sys.argv[2]).write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
