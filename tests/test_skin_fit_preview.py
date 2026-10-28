"""Independent playback never starts anatomy work, changes history or replaces saved skin."""

from dataclasses import asdict, replace

import numpy as np
import pytest

from anthroforge.application.skin_fit_preview import displayed
from anthroforge.native import skin_fit_playback, topology
from tests.test_skin_fit_jobs import fit, setup


def test_preview_supersedes_values_without_anatomy_mutation(session):
    item = fit(session, setup(session))
    before = session.document
    history, resources = tuple(session.history.entries), set(session.assets)
    for value in (0.02, 0.05, 0.15):
        session.command("skin.fit.preview", identity=item.id, value=value)
    session.wait()
    candidate = displayed(session)
    assert candidate.value == 0.15 and session.document is before
    assert tuple(session.history.entries) == history and set(session.assets) == resources
    verify_playback(session, item, candidate)
    session.command("skin.fit.preview.cancel")
    assert displayed(session) is None


def verify_playback(session, item, candidate):
    reference = session.assets[item.reference].mesh
    expected = skin_fit_playback.evaluate(
        session.engine, session.resources.skin[item.data].arrays, candidate.value
    )
    np.testing.assert_allclose(candidate.mesh.array(0), expected, atol=1e-12)
    assert topology.same_topology(reference, candidate.mesh)


def test_saved_fit_retains_playback_when_original_skin_is_missing(session):
    item = fit(session, setup(session))
    session.replace_document(skin=replace(session.document.skin, reference=""))
    assert session.command("skin.fit.inspect", identity=item.id)["stale"]
    session.command("skin.fit.preview", identity=item.id, value=-100)
    session.wait()
    assert displayed(session) is not None
    session.command("skin.fit.remove", identity=item.id)
    assert displayed(session) is None
    session.command("undo")
    assert session.document.skin.fits == (item,)


def test_fit_marks_source_motion_stale_and_invalid_preview_keeps_display(session):
    identity = setup(session)
    item = fit(session, identity)
    assert not session.command("skin.fit.inspect", identity=item.id)["stale"]
    session.command("skin.fit.preview", identity=item.id, value=0)
    session.wait()
    before = displayed(session)
    with pytest.raises(ValueError, match="finite"):
        session.command("skin.fit.preview", identity=item.id, value=float("nan"))
    assert displayed(session) is before
    reference = session.document.shortcuts[0].reference
    session.command("shortcut.set", reference=asdict(reference), value=0.1)
    session.wait()
    assert session.command("skin.fit.inspect", identity=item.id)["stale"]
