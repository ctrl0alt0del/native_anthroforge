"""Compare native annulus selection against recorded addon results."""

import json
import sys
from pathlib import Path

import numpy as np

from anthroforge.native import skin_annuli, skin_loops
from anthroforge.native.mesh import GeometryEngine
from tools.check_skin_decimation import mesh


def capture(row):
    samples = np.array([np.column_stack((x["points"], x["normals"])) for x in row["loops"]])
    count = len(samples)
    return skin_loops.Loops(
        samples,
        np.arange(count),
        np.array([[0, 1]]),
        np.zeros(count),
        np.array([x["symmetric"] for x in row["loops"]]),
    )


def evaluate(engine, row):
    surface = mesh(engine, np.array(row["vertices"]), np.array(row["faces"]))
    loops = capture(row)
    result = skin_annuli.build(surface, loops, [0, 0, 0, 1, 0, 0])
    return surface, loops, result


def correspondence(points, reference):
    choices = []
    for reverse in (False, True):
        candidate = reference[:, ::-1] if reverse else reference
        for shift in range(points.shape[1]):
            shifted = np.roll(candidate, shift, axis=1)
            choices.append(
                (float(np.max(np.linalg.norm(points - shifted, axis=2))), reverse, shift)
            )
    return min(choices)


def check(engine, row):
    _, _, result = evaluate(engine, row)
    snapshot = result.snapshot()
    points = snapshot.samples[:, :3].reshape(5, -1, 3)
    error, reversed_order, shift = correspondence(points, np.array(row["chosen"]["points"]))
    return dict(
        kind=row["kind"],
        error=error,
        reversed=reversed_order,
        shift=shift,
        metadata=snapshot.patches.tolist(),
        addon_inversions=row["chosen"]["inversions"],
    )


def main():
    rows = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["cases"]
    engine = GeometryEngine()
    results = [check(engine, row) for row in rows]
    Path(sys.argv[2]).write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
