"""Read-only transverse crossing checks on the actual comparison meshes."""

import json
from collections import Counter

import numpy as np
from fixture import OUT

from anthroforge.core.entities import IDENTITY
from anthroforge.native import inspection
from anthroforge.native.mesh import GeometryEngine


def scan(engine, tag, stage):
    file = (
        OUT.parent / (tag + "-" + stage + ".npz")
        if tag == "before"
        else OUT / (tag + "-" + stage + ".npz")
    )
    data = np.load(file)
    mesh = engine.create_mesh(
        data["points"], data["triangles"].ravel(), np.arange(len(data["triangles"]) + 1) * 3
    )
    ids, _, truncated = inspection.findings(mesh, IDENTITY, [], [], 4096, 0)
    counts = Counter(row[0] for row in ids)
    return dict(degenerate=counts[1], self_crossing_pairs=counts[2], truncated=truncated)


def run():
    engine = GeometryEngine()
    result = {
        tag: {stage: scan(engine, tag, stage) for stage in ("base", "final")}
        for tag in ("before", "current", "improved", "routed_endpoints")
    }
    (OUT / "geometry-findings.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result))


if __name__ == "__main__":
    run()
