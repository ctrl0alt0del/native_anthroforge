"""Reusable accepted-base preparation preserves numerical and ownership contracts."""

import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace

import numpy as np
import pytest

from anthroforge.core.tissue_settings import TissuePart, TissueSide
from anthroforge.native import construction, tissue_parts, tissue_preparation
from anthroforge.native.mesh import NativeCancellation, doubles, pointer
from anthroforge.native.tissue_inflation import Inflation, pack
from anthroforge.native.tissue_shapes import owned
from tests.test_tissue_inflation import FIXTURE, grid_mesh, settings

CASES = json.loads(FIXTURE.read_text())["cases"]


def unprepared(mesh, parts):
    values = (Inflation * len(parts))(*(pack(p.a.inflation, False) for p in parts))
    connectors = doubles([(p.connector_width, p.connector_fullness) for p in parts])
    handle = mesh.engine.library.af_tissue_inflate_parts(
        mesh.handle, values, len(parts), pointer(connectors), False, 0
    )
    return owned(mesh.engine, handle)


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["name"])
def test_preparation_preserves_changed_settings_and_both_sides(session, case):
    base = grid_mesh(session.engine, case["points"])
    for amount in (0.02, 0.04, 0, 0.01):
        config = replace(settings(case["settings"]), amount=amount)
        parts = (TissuePart("main", TissueSide(config)),)
        expected = unprepared(base, parts)
        actual = tissue_parts.evaluate(base, parts, "a", False)
        np.testing.assert_array_equal(actual.array(0), expected.array(0))
        np.testing.assert_array_equal(actual.array(3), expected.array(3))
        reverse = tissue_parts.evaluate(base, parts, "a", True)
        assert np.isfinite(reverse.array(0)).all()


def prepared_input(session):
    case = CASES[-1]
    base = grid_mesh(session.engine, case["points"])
    config = settings(case["settings"])
    return base, (TissuePart("main", TissueSide(config)),)


def test_changed_geometry_clearing_and_budget_do_not_reuse_stale_preparation(session):
    base, parts = prepared_input(session)
    original = tissue_parts.evaluate(base, parts, "a", False)
    moved = construction.deformed(base, base.array(0) + (0.01, 0.02, 0.03))
    output = tissue_parts.evaluate(moved, parts, "a", False)
    np.testing.assert_array_equal(output.array(0), unprepared(moved, parts).array(0))
    assert not np.array_equal(output.array(0), original.array(0))
    cache = session.engine.tissue_preparations
    assert len(cache.retained()) == 2 and cache.bytes > 0
    cache.clear()
    cache.budget = 1
    tissue_parts.evaluate(base, parts, "a", False)
    assert not cache.retained() and cache.bytes == 0


def test_cancelled_capture_and_concurrent_reads_preserve_input(session):
    base, parts = prepared_input(session)
    token = NativeCancellation(session.engine)
    token.set()
    with pytest.raises(ValueError, match="[Cc]ancel"):
        tissue_parts.evaluate(base, parts, "a", False, token.handle)
    assert not session.engine.tissue_preparations.retained()
    expected = unprepared(base, parts).array(0).copy()
    with ThreadPoolExecutor(2) as pool:
        jobs = [pool.submit(tissue_parts.evaluate, base, parts, "a", False) for _ in range(4)]
        for job in jobs:
            np.testing.assert_array_equal(job.result().array(0), expected)


def test_native_context_rejects_incompatible_mode(session):
    base, parts = prepared_input(session)
    values = (Inflation * 1)(pack(parts[0].a.inflation, False))
    prepared = tissue_preparation.acquire(base, values, 0)
    values[0].mode = 1
    handle = session.engine.library.af_tissue_inflate_prepared(
        prepared.handle, values, 1, pointer(doubles([(0.25, 0)])), False, 0, True
    )
    with pytest.raises(ValueError, match="mode changed"):
        session.engine.check(not handle)


def test_draft_envelope_sides_match_complete_published_geometry(session):
    base, parts = prepared_input(session)
    draft = [
        tissue_parts.evaluate(base, parts, "a", r, envelope=True, complete=False)
        for r in (False, True)
    ]
    full = [tissue_parts.evaluate(base, parts, "a", r, envelope=True) for r in (False, True)]
    assert all(not mesh.prepared for mesh in draft) and all(mesh.prepared for mesh in full)
    result = tissue_parts.compose(*draft, False)
    expected = tissue_parts.compose(*full, False)
    assert result.prepared
    np.testing.assert_array_equal(result.array(0), expected.array(0))
    np.testing.assert_array_equal(result.array(3), expected.array(3))
