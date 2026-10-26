"""Capture production addon transition policies in background Blender."""

import importlib
import json
import sys
from pathlib import Path

import bpy
import numpy as np

CONFIGURATIONS = (
    (40, 36, False),
    (60, 24, False),
    (48, 32, True),
    (32, 32, True),
    (41, 37, False),
    (41, 36, False),
    (50, 32, True),
    (96, 24, True),
)


def ring(count, radius, offset):
    t = np.linspace(0, 2 * np.pi, count, endpoint=False)
    return np.column_stack(
        (radius * np.sin(t) + offset, 0.03 * np.cos(2 * t), 0.8 * radius * np.cos(t))
    )


def record(instant, first, second, symmetric):
    plane = instant.SymmetryPlane(np.zeros(3), np.array([1, 0, 0])) if symmetric else None
    row = dict(first=first.tolist(), second=second.tolist(), symmetric=symmetric)
    try:
        result = instant.make_transition("fixture", (first, second), 8.0, plane)
        row.update(
            points=result.vertices.tolist(),
            faces=result.faces.tolist(),
            diagnostics=result.diagnostics,
        )
    except (ValueError, RuntimeError) as error:
        row["error"] = str(error)
    return row


def cases(instant):
    values = []
    for a, b, symmetric in CONFIGURATIONS:
        offset = 0 if symmetric else 2
        values.append(record(instant, ring(a, 1.0, offset), ring(b, 0.7, offset), symmetric))
    values.append(record(instant, ring(32, 1, 0), ring(32, 0.7, 2), True))
    values.append(record(instant, ring(40, 1, 2), ring(36, 0.7, 2.8), False))
    return values


def main():
    args = sys.argv[sys.argv.index("--") + 1 :]
    sys.path.insert(0, args[0])
    importlib.import_module("adapters.draft_skin.vendor").ensure_worker_dependencies()
    instant = importlib.import_module("adapters.topology.engine.instant")
    data = dict(blender=bpy.app.version_string, cases=cases(instant))
    Path(args[1]).write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
    print([row.get("diagnostics", row.get("error")) for row in data["cases"]])


if __name__ == "__main__":
    main()
