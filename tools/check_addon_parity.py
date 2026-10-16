"""Compare native capture and propagation with independently captured Blender matrices."""

import json
import sys
from dataclasses import replace
from pathlib import Path
from threading import Event

import numpy as np

from anthroforge.core.entities import SCP, Attachment
from anthroforge.native.attachments import capture, propagate
from anthroforge.native.mesh import GeometryEngine


def compare(engine, mesh, case):
    parent = SCP("Parent", asset="mesh", matrix=tuple(case["initial"]["parent"]))
    child = SCP(
        "Child",
        parent=parent.id,
        asset="mesh",
        matrix=tuple(case["initial"]["child"]),
        attachment=Attachment(**case["settings"]),
    )
    child = capture(engine, child, parent, {"mesh": mesh})
    parent = replace(parent, matrix=tuple(case["target"]))
    actual = propagate(engine, [parent, child], {"mesh": mesh}, {child.id}, Event())[1]
    error = float(np.max(np.abs(np.array(actual.matrix) - case["expected"])))
    return dict(error=error, settings=case["settings"], target=case["target"])


def run(path):
    data = json.loads(path.read_text())
    engine = GeometryEngine()
    faces = np.array(data["faces"], dtype=np.int64)
    mesh = engine.create_mesh(data["vertices"], faces.ravel(), np.arange(len(faces) + 1) * 3)
    results = [compare(engine, mesh, case) for case in data["cases"]]
    failed = [value for value in results if value["error"] > 3e-5]
    summary = dict(cases=len(results), failed=failed, max_error=max(r["error"] for r in results))
    path.with_suffix(".comparison.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary))
    return bool(failed)


if __name__ == "__main__":
    raise SystemExit(run(Path(sys.argv[1])))
