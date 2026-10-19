"""Relaxation uses native owned stages, exact goals and independent convergence reporting."""

import numpy as np
import pytest

from tests.test_anchor_operations import scene
from tests.test_fiber_creation import bind
from tests.test_surface_workflow import curve
from tests.test_tissue_shape_workflow import create
from tests.test_tissue_workflow import assembly, mesh, roundtrip


def shell(session):
    _, source, _ = assembly(session)
    return create(session, source)


def relaxation(session, target, mode, **settings):
    session.command("tissue.relaxation", target=target, changes=dict(mode=mode, **settings))
    session.wait()
    return session.document.object(target)


@pytest.mark.parametrize("mode", ["GEOMETRIC", "STATIC_PBD"])
def test_shell_relaxes_preserving_exact_backing_and_reuses_rest(session, mode):
    key = shell(session)
    before = session.document.object(key)
    rest = mesh(session, key)
    result = relaxation(session, key, mode, sagginess=0.5, iterations=12, gravity=(1, 0, -1))
    assert result.result.status == "ready", session.scheduler.errors
    assert result.base_result == before.base_result and result.rest_result == before.rest_result
    count = len(rest) // 2
    np.testing.assert_array_equal(mesh(session, key)[count:], rest[count:])
    assert not np.array_equal(mesh(session, key)[:count], rest[:count])
    assert result.diagnostics[0].max_fixed_error == 0


def test_conflicting_fixed_region_fails_and_retains_accepted_output(session):
    key = shell(session)
    before = mesh(session, key)
    constraint = session.command("tissue.constraint.add", target=key, mask="BACKING", offset=0.01)
    session.wait()
    item = session.document.object(key)
    assert item.intrinsic_result.status == "failed"
    assert "Contradictory" in item.intrinsic_result.error
    np.testing.assert_array_equal(session.assets[item.result.asset].mesh.array(0), before)
    session.command("tissue.constraint.remove", target=key, constraint=constraint)
    session.wait()
    np.testing.assert_array_equal(mesh(session, key), before)


@pytest.mark.parametrize("mode", ["GEOMETRIC", "STATIC_PBD"])
def test_curve_relaxation_pins_backing_and_endpoints(session, mode):
    parent, _, _ = scene(session)
    key = create(session, bind(session, parent, curve(session, 0)).id)
    before = mesh(session, key)
    for mask in ("BACKING", "ENDPOINTS"):
        session.command("tissue.constraint.add", target=key, mask=mask)
    item = relaxation(session, key, mode, iterations=12)
    assert item.result.status == "ready", session.scheduler.errors
    size = item.parts[0].a.inflation.segments
    after = mesh(session, key)
    np.testing.assert_array_equal(after[::size], before[::size])
    np.testing.assert_array_equal(after[size - 1 :: size], before[size - 1 :: size])
    np.testing.assert_array_equal(after[:size], before[:size])
    np.testing.assert_array_equal(after[-size:], before[-size:])


def test_point_geometric_relaxation_resolves_its_anchor_surface(session):
    _, _, anchor = scene(session)
    key = create(session, anchor.id)
    session.command("tissue.inflation", target=key, changes=dict(amount=0.25))
    session.wait()
    before = mesh(session, key)
    item = relaxation(session, key, "GEOMETRIC", iterations=12, sag_limit=0.05)
    assert item.result.status == "ready", session.scheduler.errors
    assert not np.array_equal(mesh(session, key), before)
    assert item.diagnostics[0].iterations <= 12


def test_iteration_limit_is_usable_warned_and_roundtrips(session, tmp_path):
    key = shell(session)
    item = relaxation(session, key, "STATIC_PBD", iterations=1, tolerance=1e-12)
    assert item.diagnostics[0].status == "ITERATION_LIMIT"
    assert item.result.status == "ready"
    roundtrip(session, tmp_path / "relaxed.anthroforge")
    assert session.document.object(key).diagnostics == item.diagnostics
    item = relaxation(session, key, "NONE")
    assert item.diagnostics[0].status == "NOT_APPLICABLE"


def test_zero_custom_thickness_field_remains_authoritative(session):
    key = shell(session)
    item = session.document.object(key)
    base = session.assets[item.base_result.asset].mesh.array(0).copy()
    session.command("tissue.field.set", target=key, name="INFLATION", values=[0.0] * len(base))
    session.wait()
    output = mesh(session, key)
    np.testing.assert_array_equal(output[: len(base)], base)
    np.testing.assert_array_equal(output[len(base) :], base)


def test_fields_reject_changed_material_sampling_without_remapping(session):
    key = shell(session)
    item = session.document.object(key)
    count = session.assets[item.base_result.asset].mesh.counts[0]
    session.command("tissue.field.set", target=key, name="INFLATION", values=[0.5] * count)
    session.wait()
    before = mesh(session, key)
    session.command("tissue.configure", target=key, changes=dict(resolution=31))
    session.wait()
    item = session.document.object(key)
    assert item.rest_result.status == "failed" and "topology" in item.rest_result.error
    np.testing.assert_array_equal(session.assets[item.result.asset].mesh.array(0), before)
    session.command("tissue.field.remove", target=key, name="INFLATION")
    session.wait()
    assert session.document.object(key).result.status == "ready"
