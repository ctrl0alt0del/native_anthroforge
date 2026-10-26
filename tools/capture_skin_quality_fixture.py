"""Capture the production addon's advisory checks on compact topology examples."""

import hashlib
import importlib
import json
import sys
import types
from dataclasses import asdict
from pathlib import Path

import numpy as np


def module(root):
    package = types.ModuleType("topology_source_control")
    package.__path__ = [str(root / "core/topology")]
    sys.modules[package.__name__] = package
    return importlib.import_module(package.__name__ + ".validation")


def capture(source, row):
    points, faces = np.array(row["vertices"]), np.array(row["faces"])
    report = asdict(source.validate_topology(points, faces))
    report.update(
        components=source.component_count(len(points), faces),
        degenerate_faces=source.degenerate_count(points, faces),
        max_valence=source.max_valence(len(points), faces),
    )
    return row | dict(expected=report)


def variants(row):
    points, faces = np.array(row["vertices"]), np.array(row["faces"])
    reversed_faces = faces.copy()
    reversed_faces[0] = reversed_faces[0, ::-1]
    return [
        row,
        dict(name="reversed-face", vertices=points.tolist(), faces=reversed_faces.tolist()),
        dict(name="duplicate-face", vertices=points.tolist(), faces=faces[[0, 0, 0]].tolist()),
        dict(name="collapsed", vertices=np.zeros_like(points).tolist(), faces=faces.tolist()),
    ]


def inputs():
    assembly = json.loads(Path("tests/fixtures/skin/assembly.json").read_text())
    rows = [
        dict(name=r["name"], vertices=r["expected"]["points"], faces=r["expected"]["faces"])
        for r in assembly["cases"]
        if "expected" in r
    ]
    return variants(rows[0]) + rows[1:]


def main():
    root, output = Path(sys.argv[1]), Path(sys.argv[2])
    source = root / "core/topology/validation.py"
    data = dict(
        source=str(source),
        sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        cases=[capture(module(root), row) for row in inputs()],
    )
    output.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")


if __name__ == "__main__":
    main()
