"""Sampled bidirectional surface distance and baseline-qualified material response."""

from types import SimpleNamespace

import numpy as np
from scipy.spatial import cKDTree

from anthroforge.core.construction import Deformer, Target
from anthroforge.core.entities import IDENTITY
from anthroforge.core.shrinkwrap import Shrinkwrap
from anthroforge.core.surface_references import SurfaceReference
from anthroforge.native import shrinkwrap


def statistics(values):
    data = np.asarray(values)
    return dict(
        max=float(data.max()),
        rms=float(np.sqrt(np.mean(data * data))),
        p95=float(np.percentile(data, 95)),
        mean=float(data.mean()),
        samples=int(data.size),
    )


def mesh(engine, points, triangles):
    corners = points[triangles]
    area = np.linalg.norm(
        np.cross(corners[:, 1] - corners[:, 0], corners[:, 2] - corners[:, 0]), axis=1
    )
    usable = triangles[area > 1e-20]
    return engine.create_mesh(points, usable.ravel(), np.arange(len(usable) + 1) * 3)


def distance(engine, points, target):
    binding = Deformer(
        "SHRINKWRAP", "", Target("probe"), shrinkwrap=Shrinkwrap(SurfaceReference("target"))
    )
    provider = SimpleNamespace(resource=SimpleNamespace(mesh=target), frame=IDENTITY)
    projected = shrinkwrap.deform(engine, points, binding, IDENTITY, provider, 0)
    return np.linalg.norm(points - projected, axis=1)


def surface(engine, a, b):
    left, right = mesh(engine, *a), mesh(engine, *b)
    samples_a = np.concatenate((a[0], a[0][a[1]].mean(axis=1)))
    samples_b = np.concatenate((b[0], b[0][b[1]].mean(axis=1)))
    return statistics(
        np.concatenate((distance(engine, samples_a, right), distance(engine, samples_b, left)))
    )


def response(original_a, current_a, original_b, current_b):
    if original_a.shape != current_a.shape or original_b.shape != current_b.shape:
        return dict(available=False, reason="Topology/sample-count changed")
    distances, indices = cKDTree(original_b).query(original_a)
    if distances.max() > 1e-5:
        return dict(
            available=False,
            reason="Baseline vertices lack close correspondence",
            gap=float(distances.max()),
        )
    return mapped_response(
        current_a - original_a, current_b[indices] - original_b[indices], distances, indices
    )


def mapped_response(delta_a, delta_b, distances, indices):
    return dict(
        available=True,
        error=statistics(np.linalg.norm(delta_a - delta_b, axis=1)),
        app_motion=statistics(np.linalg.norm(delta_a, axis=1)),
        blender_motion=statistics(np.linalg.norm(delta_b, axis=1)),
        correspondence_gap=float(distances.max()),
        unique_targets=len(np.unique(indices)),
    )


def endpoints(original_a, current_a, original_b, current_b):
    a, b = current_a[[0, -1]], current_b[[0, -1]]
    before_a, before_b = original_a[[0, -1]], original_b[[0, -1]]
    return dict(
        baseline=np.linalg.norm(before_a - before_b, axis=1).tolist(),
        edited=np.linalg.norm(a - b, axis=1).tolist(),
        response=np.linalg.norm((a - before_a) - (b - before_b), axis=1).tolist(),
    )
