from dataclasses import asdict

import numpy as np

from anthroforge.core.construction import BodyPiece, Curve, CurvePoint, ResolvedPrimitive


def test_fixed_length_body_keeps_caps_on_closed_guide(session):
    curve = Curve(
        tuple(CurvePoint(position=p) for p in ((-1, 0, 0), (0, 1, 0), (1, 0, 0), (0, -1, 0))),
        closed=True,
    )
    piece = BodyPiece(curve.id, shape="BOX", fit=False, length=0.5)
    definition = ResolvedPrimitive("BODY", curves=(curve,), pieces=(piece,), samples=5)
    key = session.command("primitive.create", kind="BODY", definition=asdict(definition))
    session.wait()
    mesh = session.assets[session.document.entity(key).asset].mesh
    faces = mesh.array(3)
    edges = np.sort(np.concatenate((faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]])), axis=1)
    edge_count = len(np.unique(edges, axis=0))
    assert mesh.counts[0] - edge_count + len(faces) == 2
    assert not session.scheduler.errors
