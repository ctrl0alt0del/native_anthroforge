"""Intentional station coalescence removes only donor floating-point zero-width strips."""

import numpy as np


def canonical(case):
    points, mapping = [], []
    for point in np.asarray(case["vertices"]):
        found = next((i for i, p in enumerate(points) if np.linalg.norm(p - point) < 1e-12), None)
        mapping.append(len(points) if found is None else found)
        if found is None:
            points.append(point)
    faces = [list(dict.fromkeys(mapping[i] for i in face)) for face in case["faces"]]
    return np.asarray(points), [face for face in faces if len(face) >= 3]
