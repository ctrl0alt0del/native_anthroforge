"""Historical 0.1.5 Body experiment; run at its original revision, before first-class curves.

This preserves the measured alternative, not a current production or acceptance evaluator.
Current qualification uses construction_profile_qualification.py and the release gate.
"""

import argparse
import json
from dataclasses import replace
from pathlib import Path

import numpy as np
from standalone_audit import measure

from anthroforge.application.construction_evaluator import Evaluation
from anthroforge.application.primitive_operations import default_primitive
from anthroforge.application.session import Session
from anthroforge.core.document import Document
from anthroforge.core.entities import IDENTITY, SCP
from anthroforge.native import bodies
from anthroforge.native.mesh import NativeCancellation


def fixture(session, samples, sides):
    primitive = default_primitive("BODY", "CAPSULE")
    piece = replace(primitive.pieces[0], sides=sides)
    primitive = replace(primitive, samples=samples, pieces=(piece,))
    entity = SCP("Body", primitive=primitive)
    document, cancel = Document(entities=(entity,)), NativeCancellation(session.engine)
    evaluator = Evaluation(session.engine, document, {}, cancel)
    previous = evaluator.geometry(entity)
    return replace(entity, asset="previous"), previous, cancel


class CachedIdentityBody:
    def __init__(self, session, entity, cancel):
        self.session, self.entity, self.cancel = session, entity, cancel
        self.definition = entity.primitive
        self.piece, self.curve = self.definition.pieces[0], self.definition.curves[0]
        assert len(self.definition.pieces) == 1 and not entity.deformers and not entity.thickness
        assert self.curve.matrix == IDENTITY and not self.curve.closed
        self.base = bodies.base(
            session.engine, self.piece, self.definition.samples, False, cancel.handle
        )

    def compute(self, evaluator, entity):
        samples = evaluator.curve(entity, entity.primitive.curves[0], entity.primitive)
        return bodies.bend(self.base, samples, self.piece, False, self.cancel.handle)


def changed_entity(entity, step):
    curve = entity.primitive.curves[0]
    first = replace(curve.points[0], position=(-0.5, step * 0.003, 0.0))
    changed = replace(curve, points=(first, *curve.points[1:]))
    return replace(entity, primitive=replace(entity.primitive, curves=(changed,)))


def verify_geometry(expected, actual):
    assert expected.counts == actual.counts
    for kind in range(5):
        np.testing.assert_allclose(expected.array(kind), actual.array(kind), rtol=0, atol=1e-12)
    np.testing.assert_allclose(expected.bounds, actual.bounds, rtol=0, atol=1e-12)
    ray = ([0, 0, 2], [0, 0, -1])
    a = expected.engine.pick(expected, IDENTITY, *ray)
    b = actual.engine.pick(actual, IDENTITY, *ray)
    assert (a is None) == (b is None)
    if a:
        np.testing.assert_allclose(a, b, rtol=0, atol=1e-12)


def evaluator(session, entity, previous, cancel):
    return Evaluation(session.engine, Document(entities=(entity,)), {"previous": previous}, cancel)


def verify_positions(session, entity, previous, cancel, candidate):
    for step in range(8):
        item = changed_entity(entity, step)
        worker = evaluator(session, item, previous, cancel)
        verify_geometry(worker.geometry(item), candidate.compute(worker, item))


def comparison_runs(worker, entity, candidate):
    calls = dict(
        current=lambda: worker.geometry(entity), cached=lambda: candidate.compute(worker, entity)
    )
    return [
        dict(mode=mode, **measure(calls[mode], 12))
        for mode in ("current", "cached", "cached", "current")
    ]


def comparison(session, samples, sides):
    entity, previous, cancel = fixture(session, samples, sides)
    candidate = CachedIdentityBody(session, entity, cancel)
    verify_positions(session, entity, previous, cancel, candidate)
    item = changed_entity(entity, 5)
    worker = evaluator(session, item, previous, cancel)
    return dict(
        samples=samples,
        sides=sides,
        vertices=previous.counts[0],
        triangles=previous.counts[3],
        runs=comparison_runs(worker, item, candidate),
    )


def record_calls(session, output):
    entity, previous, cancel = fixture(session, 32, 16)
    worker = evaluator(session, entity, previous, cancel)
    session.command("profile.start")
    for _ in range(3):
        worker.geometry(entity)
    session.command("profile.stop", path=str(output / "body-stages.afprofile.zip"), wait=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    session = Session()
    try:
        results = [comparison(session, n, sides) for n, sides in ((32, 16), (128, 32), (256, 64))]
        record_calls(session, args.output.resolve())
        (args.output / "geometry.json").write_text(json.dumps(results, indent=2) + "\n")
        print(json.dumps(results))
    finally:
        session.close()


if __name__ == "__main__":
    main()
