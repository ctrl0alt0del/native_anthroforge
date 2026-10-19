"""Pinned addon outputs, canonical topology, cancellation and explicit correspondence."""

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.curve_engines import PolylineSettings
from anthroforge.core.curve_uses import CurveUse
from anthroforge.core.entities import IDENTITY
from anthroforge.native import curve_surfaces as surface
from anthroforge.native import paths, topology
from anthroforge.native.mesh import NativeCancellation

FIXTURE = json.loads((Path(__file__).parent / "fixtures/surfaces/addon.json").read_text())


@pytest.fixture
def engine(session):
    return session.engine


def row(engine, points, closed=False, samples=5):
    curve = Curve(
        tuple(CurvePoint(position=tuple(p)) for p in points),
        closed=closed,
        engine_settings=PolylineSettings(),
    )
    return surface.row(paths.evaluate(engine, curve), IDENTITY, CurveUse(curve.id, samples=samples))


def aligned(engine, rows, settings):
    alignment, across = surface.layout(engine, rows, settings)
    for source, values in zip(rows, alignment, strict=True):
        source.origin, source.alignment_reverse = values[0], int(values[1])
    return across


def faces(mesh):
    corners, offsets = mesh.array(1), mesh.array(2)
    return [corners[a:b].tolist() for a, b in zip(offsets, offsets[1:], strict=False)]


@pytest.mark.parametrize("case", FIXTURE["cases"], ids=lambda value: value["name"])
def test_native_surface_matches_donor(engine, case):
    rows = [row(engine, points, case["closed"], case["samples"]) for points in case["rows"]]
    settings = surface.Settings(
        exact=case["exact"], patch=case["patch"], patch_resolution=case["patch_resolution"]
    )
    across = aligned(engine, rows, settings)
    mesh = surface.geometry(engine, rows, across, settings)
    np.testing.assert_allclose(mesh.array(0), case["vertices"], atol=1e-10)
    assert faces(mesh) == case["faces"]
    complete = topology.finalize(mesh, None, 0)
    assert complete.counts[3] > 0


def test_surface_ranges_and_reversal_preserve_corners(engine):
    points = [[0, 0, 0], [0.1, 0, 0], [1, 0, 0]]
    rows = [row(engine, points), row(engine, np.array(points) + [0, 1, 0])]
    for source in rows:
        source.start, source.span, source.reverse = 0.2, 0.5, 1
    settings = surface.Settings(strips=1)
    mesh = surface.geometry(engine, rows, aligned(engine, rows, settings), settings)
    np.testing.assert_allclose(mesh.array(0), [[0.8, 0, 0], [0.3, 0, 0], [0.8, 1, 0], [0.3, 1, 0]])


def test_surface_cancellation_and_incompatible_ranges(engine):
    data = FIXTURE["cases"][2]["rows"]
    rows = [row(engine, points, True) for points in data]
    token = NativeCancellation(engine)
    token.set()
    with pytest.raises(ValueError, match="[Cc]ancel"):
        surface.layout(engine, rows, surface.Settings(), token.handle)
    rows[1].span = 0.5
    with pytest.raises(ValueError, match="[Ii]ncompatible"):
        surface.layout(engine, rows, surface.Settings())


def test_surface_flip_and_geometry_budget(engine):
    rows = [row(engine, points) for points in FIXTURE["cases"][0]["rows"]]
    settings = surface.Settings(strips=1)
    across = aligned(engine, rows, settings)
    normal = surface.geometry(engine, rows, across, settings)
    flipped = surface.geometry(engine, rows, across, replace(settings, flip=True))
    assert faces(flipped) == [[face[0], *reversed(face[1:])] for face in faces(normal)]
    with pytest.raises(ValueError, match="budget"):
        surface.geometry(engine, rows, [262144], settings)


def test_closed_deformation_keeps_explicit_correspondence_until_realign(engine):
    data = FIXTURE["cases"][2]["rows"]
    rows = [row(engine, points, True) for points in data]
    settings = surface.Settings(strips=1)
    across = aligned(engine, rows, settings)
    before = (rows[1].origin, rows[1].alignment_reverse)
    rows[1].matrix = (surface.c.c_double * 16)(-1, 0, 0, 1, 0, -1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1)
    mesh = surface.geometry(engine, rows, across, settings)
    np.testing.assert_allclose(mesh.array(0)[4], [1, 1, 0.3])
    assert (rows[1].origin, rows[1].alignment_reverse) == before
    rows[1].origin, rows[1].alignment_reverse = -1, 0
    realigned = surface.geometry(engine, rows, aligned(engine, rows, settings), settings)
    np.testing.assert_allclose(realigned.array(0)[4], [0, 0, 0.3])
