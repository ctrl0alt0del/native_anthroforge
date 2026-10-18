"""Serial preparation benchmarks; use PYTHONPATH to compare preserved source revisions."""

import argparse
import hashlib
import json
from dataclasses import replace
from pathlib import Path
from statistics import median
from time import perf_counter
from types import SimpleNamespace

import numpy as np

from anthroforge.application.session import Session
from anthroforge.core.construction import Control, Curve, CurvePoint, Deformer, Target
from anthroforge.core.document import Document
from anthroforge.core.entities import IDENTITY
from anthroforge.desktop import authoring_actions, authoring_lines
from anthroforge.native import components, construction, curve_queries


def measure(call, repeats=25):
    call()
    samples = []
    for _ in range(repeats):
        start = perf_counter()
        result = call()
        samples.append((perf_counter() - start) * 1000)
    array = np.asarray(result, dtype=np.float64)
    return dict(
        median_ms=median(samples),
        samples_ms=samples,
        shape=list(array.shape),
        checksum=hashlib.sha256(array.round(10).tobytes()).hexdigest(),
    )


def cage_fixture(session):
    points = construction.lattice_grid(session.engine, (10, 10, 10))
    frame = session.engine.transform([1, 2, 3, 10, 20, 30, 2, 1, 3])
    cage = Control(
        "Cage", "LATTICE", points=tuple(map(tuple, points)), resolution=(10, 10, 10), matrix=frame
    )
    session.document = Document(controls=(cage,), update_mode="MANUAL")
    return cage


def conversion_case(session, cage):
    world = components.transformed(session.engine, cage.points, cage.matrix)
    rows = [(dict(owner=cage.id, index=i, part="lattice"), p, p) for i, p in enumerate(world)]
    editor = SimpleNamespace(controller=SimpleNamespace(session=session), drag_rows=rows)
    updates = []
    session.command = lambda operation, **args: updates.append(args["position"])

    def convert():
        updates.clear()
        authoring_actions.apply_points(editor, world)
        return updates

    return convert


def curve_fixture():
    points = tuple(CurvePoint(position=(i * 0.01, i % 3 * 0.02, 0)) for i in range(1000))
    return Curve(points, closed=True)


def cases(session):
    engine, cage = session.engine, cage_fixture(session)
    curve = curve_fixture()
    return dict(
        **hook_cases(engine),
        cage_lines=lambda: authoring_lines.cage_lines(session, cage),
        curve_cubics=lambda: curve_queries.cubics(engine, curve, IDENTITY),
        component_conversion=conversion_case(session, cage),
    )


def hook_cases(engine):
    points = np.random.default_rng(12).normal(size=(100000, 3))
    binding = Deformer("HOOK", "hook", Target("owner"))
    weighted = replace(
        binding,
        weights=tuple(np.linspace(0, 1, len(points))),
        indices=tuple(range(0, len(points), 3)),
        restrict=True,
        invert=True,
    )
    target = engine.transform([1, 2, 3, 0, 0, 0, 1, 1, 1])
    return dict(
        hook_default=lambda: construction.hook(engine, points, binding, IDENTITY, target, 0),
        hook_weighted=lambda: construction.hook(engine, points, weighted, IDENTITY, target, 0),
    )


def recording(session, calls, path):
    session.profiler.start()
    try:
        for _ in range(3):
            for name, call in calls.items():
                session.profiler.call("boundary_audit", name, call)
    finally:
        session.profiler.stop(str(path), wait=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    session = Session()
    try:
        calls = cases(session)
        result = {name: measure(call) for name, call in calls.items()}
        recording(session, calls, args.output.with_suffix(".afprofile.zip"))
        args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    finally:
        session.close()


if __name__ == "__main__":
    main()
