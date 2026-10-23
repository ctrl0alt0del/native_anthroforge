"""Reproduce Humerus parity and history on the unchanged migrated muscle assembly."""

import sys
from contextlib import closing
from pathlib import Path
from time import perf_counter

import numpy as np
from qualify_retained_attachment_edits import bindings, history, load
from shortcut_parity_app_capture import capture, edit
from shortcut_parity_compare import compare_object, dataset
from shortcut_parity_plan import read, write

from anthroforge.application.session import Session
from anthroforge.native.components import transformed
from anthroforge.native.scene import entity_frame


def anchor(session, item):
    return transformed(
        session.engine, item.attachment.binding[18:21], entity_frame(session.engine, item)
    )[0]


def exercise(session, case, output):
    initial = session.document
    child = initial.entity("SCP_13")
    original_anchor, fiber_bindings = anchor(session, child), bindings(session)
    from qualify_retained_attachment_edits import positions

    shapes, start = positions(session), perf_counter()
    edit(session, case)
    capture(session, output / "app" / case["id"], perf_counter() - start)
    result = verify(session, initial, original_anchor, fiber_bindings)
    result["undo_tissue_error"] = history(session, fiber_bindings, shapes)
    assert session.document.entity(child.id).attachment == child.attachment
    session.command("save", path=str(output / "humerus-edited.anthroforge"), blocked_policy="wait")
    return result


def verify(session, initial, original_anchor, fiber_bindings):
    current = session.document.entity("SCP_13")
    error = float(np.linalg.norm(anchor(session, current) - original_anchor))
    assert error < 1e-10, error
    assert not session.scheduler.errors, session.scheduler.errors
    assert bindings(session) == fiber_bindings
    assert all(e.attachment == initial.entity(e.id).attachment for e in session.document.entities)
    assert all(e.status == "ready" for e in session.document.entities)
    return dict(
        anchor_displacement=error, bone_bindings_preserved=True, fiber_bindings_preserved=True
    )


def compare(session, prior, output, name):
    initial = dataset(prior, "app", "baseline"), dataset(prior, "blender", "baseline")
    left, right = dataset(output, "app", name), dataset(prior, "blender", name)
    keys = left[0]["lookup"].keys() & right[0]["lookup"].keys()
    rows = [compare_object(session.engine, k, left, right, initial) for k in sorted(keys)]
    write(output / "comparison.json", dict(case=name, units="metres", rows=rows))
    humerus = next(r for r in rows if r["id"] == "SCP_13")
    assert humerus["surface_distance"]["max"] < 1e-5, humerus
    return humerus


def main(prior, output):
    plan = read(prior / "plan.json")
    case = next(c for c in plan["cases"] if c["id"] == "SHORTCUT_15")
    output.mkdir(parents=True, exist_ok=True)
    write(output / "plan.json", plan)
    with closing(Session()) as session:
        load(session, Path(plan["standalone"]))
        result = exercise(session, case, output)
        print("Assembly edit, retained bindings and history passed.", flush=True)
        result["humerus"] = compare(session, prior, output, case["id"])
        write(output / "acceptance.json", result)
        print(result["humerus"], flush=True)


if __name__ == "__main__":
    main(*(Path(value).resolve() for value in sys.argv[1:3]))
