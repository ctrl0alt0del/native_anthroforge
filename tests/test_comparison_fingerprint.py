"""Change fingerprints distinguish position and winding without face-order noise."""

from anthroforge.native.comparison import fingerprint


def mesh(engine, corners, vertices=None):
    points = vertices or [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]
    return engine.create_mesh(points, corners, [0, 3, 6])


def test_fingerprint_preserves_orientation_but_ignores_triangle_order(session):
    a = mesh(session.engine, [0, 1, 2, 0, 2, 3])
    b = mesh(session.engine, [2, 3, 0, 1, 2, 0])
    reversed_mesh = mesh(session.engine, [2, 1, 0, 3, 2, 0])
    assert fingerprint(a) == fingerprint(b)
    assert fingerprint(a) != fingerprint(reversed_mesh)


def test_fingerprint_detects_coordinate_changes(session):
    a = mesh(session.engine, [0, 1, 2, 0, 2, 3])
    b = mesh(session.engine, [0, 1, 2, 0, 2, 3], [(0, 0, 0), (1, 0, 0), (1, 1, 0.001), (0, 1, 0)])
    assert fingerprint(a) != fingerprint(b)
