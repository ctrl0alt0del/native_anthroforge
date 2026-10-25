"""Validate the experimental case and report invariants without altering production state."""

import json

import numpy as np
from fixture import OUT

from anthroforge.native import components


def rigid(context, trial):
    d = trial.data
    frame = (0.0, -1.0, 0.0, 0.3, 1.0, 0.0, 0.0, -0.4, 0.0, 0.0, 1.0, 0.2, 0.0, 0.0, 0.0, 1.0)
    current = components.transformed(context.engine, d.before, frame)
    expected = components.transformed(context.engine, d.points, frame)
    goals = components.transformed(context.engine, d.points[d.pins], frame)
    result = trial.evaluate(current, goals)
    return float(np.max(np.abs(result - expected)))


def invariants(f, trials):
    result = [invariant_row(f.after, trial) for trial in trials]
    (OUT / "invariants.json").write_text(json.dumps(result, indent=2))
    assert max(max(v.values()) for v in result) < 1e-8, result
    return result


def invariant_row(context, trial):
    d = trial.data
    neutral = trial.evaluate(d.before, d.points[d.pins])
    current = trial.evaluate(d.current, d.goals)
    return dict(
        neutral=float(np.max(np.abs(neutral - d.points))),
        rigid=rigid(context, trial),
        pins=float(np.max(np.abs(current[d.pins] - d.goals))),
    )


def production_equivalence():
    result = {}
    for stage in ("base", "rest", "intrinsic", "final"):
        a, b = (
            np.load(OUT / ("current-" + stage + ".npz")),
            np.load(OUT.parent / ("after-" + stage + ".npz")),
        )
        error = float(np.max(np.abs(a["points"] - b["points"])))
        result[stage] = dict(
            max_error=error, topology_equal=bool(np.array_equal(a["triangles"], b["triangles"]))
        )
    (OUT / "production-equivalence.json").write_text(json.dumps(result, indent=2))
    assert all(v["max_error"] == 0 and v["topology_equal"] for v in result.values())
    return result
