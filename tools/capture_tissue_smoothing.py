"""Capture the production addon height solver, including rejected configurations."""

import hashlib
import importlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np


def grid_faces(rows, cols):
    return [
        [i * cols + j, (i + 1) * cols + j, (i + 1) * cols + j + 1, i * cols + j + 1]
        for i in range(rows - 1)
        for j in range(cols - 1)
    ]


def ordinary(row):
    points, output = (np.asarray(row[k]) for k in ("points", "output"))
    rows, cols, _ = points.shape
    faces = grid_faces(rows, cols)
    return dict(
        name=row["name"],
        points=points.reshape(-1, 3).tolist(),
        output=output.reshape(-1, 3).tolist(),
        faces=faces,
        labels=[0] * len(faces),
        count=1,
        material=[rows, cols, 0, 0, rows * cols, *range(rows * cols)],
    )


def branch(row):
    records, labels, cursor, part = row["material"], [], 0, 0
    while cursor < len(records):
        rows, cols, _, _, count = records[cursor : cursor + 5]
        labels.extend([part] * ((rows - 1) * (cols - 1)))
        cursor += 5 + count
        part += 1
    keys = ("name", "points", "output", "faces", "material", "axes")
    return dict({key: row[key] for key in keys}, labels=labels, count=part)


def capture(row, smooth):
    settings = dict(radius=0.2, strength=0.8, max_change=0.03)
    base, own, faces, labels = (np.asarray(row[k]) for k in ("points", "output", "faces", "labels"))
    reports = []
    try:
        for part in range(row["count"]):
            own, report = smooth(base, own, faces, labels, part, SimpleNamespace(**settings))
            reports.append(report)
        return dict(row, settings=settings, expected=own.tolist(), reports=reports)
    except ValueError as error:
        return dict(row, settings=settings, error=str(error))


def main(addon, fixtures):
    sys.path.insert(0, str(addon))
    smooth = importlib.import_module("core.vcp.height_smoothing_native").smooth
    inputs = [ordinary(r) for r in json.loads((fixtures / "inflation.json").read_text())["cases"]]
    inputs += [branch(r) for r in json.loads((fixtures / "branches.json").read_text())["cases"]]
    files = [
        *list((addon / "native/smoothing/src").glob("*.cpp")),
        addon / "native/smoothing/af_height_smoothing_v1.dll",
    ]
    sources = {str(p.relative_to(addon)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    result = dict(sources=sources, cases=[capture(row, smooth) for row in inputs])
    (fixtures / "smoothing.json").write_text(json.dumps(result, allow_nan=False) + "\n")


if __name__ == "__main__":
    main(*(Path(value) for value in sys.argv[sys.argv.index("--") + 1 :]))
