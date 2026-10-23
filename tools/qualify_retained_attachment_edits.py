"""Read-only source qualification of the migrated assembly's three failing controls."""

import json
import sys
from contextlib import closing
from pathlib import Path
from time import perf_counter

import numpy as np

from anthroforge.application.projects import adopt, synchronize_loaded
from anthroforge.application.session import Session
from anthroforge.application.storage import read_package
from anthroforge.core.fibers import Fiber


def load(session, source):
    adopt(session, *read_package(source, session.engine))
    synchronize_loaded(session)
    session.wait(180)


def failures(session):
    return [
        dict(label=j.label, error=j.error) for j in session.scheduler.jobs if j.state == "failed"
    ]


def bindings(session):
    return {
        o.id: (o.bindings, o.attachment_asset, o.supports)
        for o in session.document.objects
        if isinstance(o, Fiber)
    }


def positions(session):
    return {
        o.id: session.assets[o.result.asset].mesh.array(0).copy()
        for o in session.document.objects
        if hasattr(o, "intrinsic_result") and o.result.asset
    }


def drift(session, before):
    current = positions(session)
    return {
        key: float(np.max(np.abs(points - current[key])))
        if points.shape == current[key].shape
        else "changed topology"
        for key, points in before.items()
    }


def set_value(session, mapping, value):
    start = perf_counter()
    session.command("shortcut.set", reference=mapping["reference"], value=value)
    session.wait(180)
    return perf_counter() - start


def history(session, initial, before):
    edited = positions(session)
    session.command("undo")
    session.wait(180)
    assert bindings(session) == initial
    result = drift(session, before)
    session.command("redo")
    session.wait(180)
    assert bindings(session) == initial
    require_shapes(drift(session, edited))
    return result


def require_shapes(values):
    assert all(isinstance(v, float) and v < 1e-8 for v in values.values()), values


def require_ready(session):
    assert not failures(session), failures(session)
    assert all(e.status == "ready" for e in session.document.entities)


def roundtrip(session, path, initial):
    session.command("save", path=str(path), blocked_policy="wait")
    session.wait(180)
    session.command("open", path=str(path))
    session.wait(180)
    assert bindings(session) == initial
    require_ready(session)


def exercise(session, mapping, output, number):
    initial, before = bindings(session), positions(session)
    elapsed = set_value(session, mapping, mapping["value"] * 1.05)
    result = dict(seconds=elapsed, failures=failures(session))
    assert bindings(session) == initial
    result["undo_drift"] = history(session, initial, before)
    roundtrip(session, output / f"edit-{number}.anthroforge", initial)
    result["restoration_seconds"] = set_value(session, mapping, mapping["value"])
    result["restoration_drift"] = drift(session, before)
    result["all_failures"] = failures(session)
    assert bindings(session) == initial
    require_shapes(result["restoration_drift"])
    require_ready(session)
    return result


def run(source, mappings, output):
    output.mkdir(parents=True, exist_ok=True)
    data = json.loads(mappings.read_text())
    for number in (15, 16, 21):
        with closing(Session()) as session:
            load(session, source)
            result = exercise(session, data[f"SHORTCUT_{number}"], output, number)
        (output / f"result-{number}.json").write_text(json.dumps(result, indent=2))
        print(
            json.dumps(
                dict(control=number, seconds=result["seconds"], failures=result["all_failures"])
            ),
            flush=True,
        )


if __name__ == "__main__":
    run(*(Path(value).resolve() for value in sys.argv[1:4]))
