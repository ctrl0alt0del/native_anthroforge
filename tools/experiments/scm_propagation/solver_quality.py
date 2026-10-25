"""Native shape findings and hard-pin checks, kept separate from timing trials."""

import json
from collections import Counter

import numpy as np
from fixture import OUT as ORIGINAL
from hybrid_retest import OUT, write

from anthroforge.core.entities import IDENTITY
from anthroforge.native import inspection
from anthroforge.native.mesh import GeometryEngine


def scan(engine, label, stage):
    data = np.load(OUT / (label + "-" + stage + ".npz"))
    q, t = data["points"], data["triangles"]
    mesh = engine.create_mesh(q, t.ravel(), np.arange(len(t) + 1) * 3)
    ids, _, truncated = inspection.findings(mesh, IDENTITY, [], [], 4096, 0)
    counts = Counter(int(row[0]) for row in ids)
    return dict(crossings=counts[2], degenerate=counts[1], truncated=truncated)


def pins(label):
    result = []
    for key in json.loads((ORIGINAL.parent / "before-paths.json").read_text()):
        file = ORIGINAL / ("current-" + key + ".npz")
        candidate = OUT / (label + "-" + key + ".npz")
        if not candidate.exists():
            continue
        expected = np.load(file)["samples"][[0, -1], :3]
        actual = np.load(candidate)["samples"][[0, -1], :3]
        result.append(float(np.max(np.linalg.norm(actual - expected, axis=1))))
    return max(result)


def run():
    engine = GeometryEngine()
    names = json.loads((OUT / "summary.json").read_text())
    result = {
        name: dict(
            stages={s: scan(engine, name, s) for s in ("base", "rest", "final")},
            max_endpoint_error=pins(name),
        )
        for name in names
    }
    assert max(v["max_endpoint_error"] for v in result.values()) < 1e-8
    write("quality.json", result)
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    run()
