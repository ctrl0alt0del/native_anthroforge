"""Typed tissue bases keep attachments, settings and accepted outputs live."""

import numpy as np
import pytest

from tests.test_anchor_operations import scene
from tests.test_fiber_creation import bind
from tests.test_surface_workflow import curve
from tests.test_tissue_workflow import assembly, mesh, roundtrip


def create(session, source):
    key = session.command("tissue.create", source=source, preset="CUSTOM")
    session.wait()
    assert session.document.object(key).result.status == "ready", session.scheduler.errors
    return key


@pytest.mark.parametrize("kind", ["POINT", "CURVE"])
def test_attached_typed_bases_update_and_reopen_without_proxy_meshes(session, tmp_path, kind):
    parent, _, anchor = scene(session)
    source = anchor.id if kind == "POINT" else bind(session, parent, curve(session, 0)).id
    key = create(session, source)
    before = mesh(session, key)
    assert session.document.object(key).base_state.kind == kind
    roundtrip(session, tmp_path / "shape.anthroforge")
    np.testing.assert_allclose(mesh(session, key), before)
    session.command("scp.transform", entity=parent, values=[0, 0, 0.2, 0, 0, 0, 1, 1, 1])
    session.wait()
    np.testing.assert_allclose(mesh(session, key), before + [0, 0, 0.2], atol=1e-8)


def test_normal_shell_preserves_source_and_structural_backing(session):
    _, source, _ = assembly(session)
    original = session.document.object(source)
    key = create(session, source)
    item = session.document.object(key)
    base = session.assets[item.base_result.asset].mesh.array(0)
    np.testing.assert_array_equal(mesh(session, key)[len(base) :], base)
    session.command("tissue.inflation", target=key, changes=dict(amount=0.15))
    session.wait()
    np.testing.assert_array_equal(mesh(session, key)[len(base) :], base)
    assert session.document.object(source) == original
