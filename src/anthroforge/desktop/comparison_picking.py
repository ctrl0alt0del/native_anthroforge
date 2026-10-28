"""Cached native queries over a comparison view's displayed revision."""

import numpy as np

from anthroforge.native import paths, scene


def capture(model):
    return {kind: batch(model, kind) for kind in ("MESH", "PATH")}


def batch(model, kind):
    rows = [r for r in model.active_rows() if r["content"]["kind"] == kind]
    return (
        rows,
        np.array([r["handle"] for r in rows], dtype=np.uint64),
        np.ascontiguousarray([r["content"]["matrix"] for r in rows], dtype=np.float64),
    )


def pick(engine, cache, origin, direction, radius):
    found = []
    for kind, (rows, handles, matrices) in (cache or {}).items():
        if not rows:
            continue
        arguments = (engine, handles, matrices, origin, direction)
        hits = scene.pick(*arguments) if kind == "MESH" else paths.pick(*arguments, radius)
        found.extend((r[1], rows[int(r[0])]) for r in hits)
    row = min(found, key=lambda hit: hit[0])[1] if found else {}
    return row.get("content", {}).get("source", row.get("id", ""))
