"""Counterfactual native pose calculation; never changes or saves an authored binding."""

import sys
from contextlib import closing
from dataclasses import replace
from pathlib import Path
from threading import Event

import numpy as np
from qualify_retained_attachment_edits import load
from shortcut_parity_app_capture import edit
from shortcut_parity_plan import read, write

from anthroforge.application.session import Session
from anthroforge.native.attachments import ordered, propagate


def probe(session, case, output):
    key = case["mapping"]["reference"]["target"]
    original = session.document.entity(key).attachment
    edit(session, case)
    changed = session.document.entity(key)
    entities = [
        replace(e, attachment=original) if e.id == key else e for e in session.document.entities
    ]
    meshes = {k: r.mesh for k, r in session.assets.items()}
    evaluated = propagate(session.engine, ordered(entities), meshes, {key}, Event())
    candidate = next(e for e in evaluated if e.id == key)
    expected = next(
        r for r in read(output / "blender" / case["id"] / "state.json")["objects"] if r["id"] == key
    )
    return outcome(key, changed, candidate, expected, original)


def outcome(key, changed, candidate, expected, original):
    return dict(
        id=key,
        normal_matrix=list(changed.matrix),
        retained_matrix=list(candidate.matrix),
        blender_matrix=expected["frame"],
        status=candidate.status,
        error=candidate.error,
        attachment_recaptured=changed.attachment != original,
        max_matrix_error=float(np.max(np.abs(np.asarray(candidate.matrix) - expected["frame"]))),
    )


def main(output):
    plan = read(output / "plan.json")
    case = next(c for c in plan["cases"] if c["id"] == "SHORTCUT_15")
    with closing(Session()) as session:
        load(session, Path(plan["standalone"]))
        result = probe(session, case, output)
        write(output / "owner-binding-counterfactual.json", result)
        print(result)


if __name__ == "__main__":
    main(Path(sys.argv[1]))
