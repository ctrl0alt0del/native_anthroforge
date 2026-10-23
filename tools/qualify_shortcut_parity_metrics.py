"""Known-answer checks for the analytical report, including metre/centimetre input."""

import numpy as np
from shortcut_parity_compare import geometry, mesh_response, physical_frame
from shortcut_parity_metrics import endpoints, response, surface

from anthroforge.core.entities import IDENTITY
from anthroforge.native.mesh import GeometryEngine


def input_data(points, scale):
    record = dict(frame=list(IDENTITY))
    return dict(scene_scale=scale, lookup={"mesh": record}), {
        "mesh__vertices": points,
        "mesh__triangles": np.asarray([[0, 1, 2]]),
    }


def units(engine, points):
    metres, centimetres = input_data(points, 1.0), input_data(points * 100, 0.01)
    a, b = geometry(metres, "mesh"), geometry(centimetres, "mesh")
    assert surface(engine, a, b)["max"] < 1e-12
    np.testing.assert_allclose(physical_frame(centimetres, "mesh")[:3, :3], np.eye(3) * 0.01)


def distances(engine, points):
    faces = np.asarray([[0, 1, 2]])
    assert surface(engine, (points, faces), (points, faces[:, ::-1]))["max"] < 1e-12
    moved = points + [0, 0, 0.125]
    np.testing.assert_allclose(surface(engine, (points, faces), (moved, faces))["max"], 0.125)


def deformation(points):
    order = [2, 0, 1]
    delta = np.asarray([0, 0, 0.125])
    result = response(points, points + delta, points[order], (points + delta)[order])
    assert result["available"] and result["error"]["max"] < 1e-12
    assert not response(points, points[:2], points, points)["available"]
    error = endpoints(points, points + delta, points, points)["response"]
    np.testing.assert_allclose(error, [0.125, 0.125])


def exclusions(points):
    duplicated = points[[0, 0, 2]]
    assert not response(duplicated, duplicated, points, points)["available"]
    a, b = (points, np.asarray([[0, 1, 2]])), (points, np.asarray([[0, 2, 1]]))
    assert not mesh_response(a, b, a, a)["available"]


if __name__ == "__main__":
    vertices = np.asarray([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    native = GeometryEngine()
    units(native, vertices)
    distances(native, vertices)
    deformation(vertices)
    exclusions(vertices)
    print("Parity metric known-answer checks passed")
