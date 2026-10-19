"""Tissues use actual attached construction, stage publications and historical state."""

import numpy as np
import pytest

from anthroforge.core.membranes import Membrane
from anthroforge.core.tissues import TissueVCP
from tests.conftest import CUBE
from tests.test_fiber_creation import bind
from tests.test_surface_workflow import curve, surface


def assembly(session):
    bone = session.command("import", path=str(CUBE), units=1.0)["entity_id"]
    session.wait()
    sources = [bind(session, bone, curve(session, y)).id for y in (0, 0.4)]
    membrane = surface(session, sources, strips=6)
    assert isinstance(session.document.object(membrane), Membrane)
    tissue = session.command("tissue.create", source=membrane)
    session.wait()
    session.command("tissue.configure", target=tissue, changes=dict(stacking=False))
    session.wait()
    return bone, membrane, tissue


def mesh(session, tissue):
    item = session.document.object(tissue)
    assert item.result.status == "ready", item.result.error
    return session.assets[item.result.asset].mesh.array(0).copy()


def test_tissue_stages_use_attached_membrane_and_settings_reuse_base(session):
    _, source, key = assembly(session)
    item = session.document.object(key)
    assert isinstance(item, TissueVCP), session.scheduler.errors
    assert item.base_result.asset and item.rest_result.asset and item.final_result.asset
    before, base = mesh(session, key), item.base_result
    membrane = session.document.object(source)
    session.command("tissue.inflation", target=key, changes=dict(amount=0.08))
    session.wait()
    assert session.document.object(key).base_result == base
    assert session.document.object(source) == membrane
    assert not np.array_equal(before, mesh(session, key))


def test_source_motion_propagates_and_generated_transform_is_rejected(session):
    bone, _, key = assembly(session)
    before = mesh(session, key)
    session.command("scp.transform", entity=bone, values=[0, 0, 0.3, 0, 0, 0, 1, 1, 1])
    session.wait()
    np.testing.assert_allclose(mesh(session, key), before + [0, 0, 0.3], atol=1e-8)
    with pytest.raises(ValueError, match="generated|derived|source"):
        session.command("object.transform", target=key, values=[1, 0, 0, 0, 0, 0, 1, 1, 1])


def test_tissue_preserves_source_on_delete_and_roundtrips_stages(session, tmp_path):
    _, source, key = assembly(session)
    before = session.document.object(key)
    path = tmp_path / "tissue.anthroforge"
    roundtrip(session, path)
    assert session.document.object(key) == before
    session.command("object.delete", target=key)
    assert source in session.document.registry.records
    session.command("undo")
    session.wait()
    np.testing.assert_allclose(
        mesh(session, key), session.assets[before.result.asset].mesh.array(0)
    )


def roundtrip(session, path):
    session.command("save", path=str(path), blocked_policy="wait")
    session.wait()
    session.command("open", path=str(path))
    session.wait()
