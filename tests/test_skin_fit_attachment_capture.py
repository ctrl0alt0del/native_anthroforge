"""Sampled skin follows real driver policies and attached construction in isolation."""

from dataclasses import replace

import numpy as np
import pytest

from anthroforge.application import skin_assets, skin_fit_capture
from anthroforge.core.skin import SkinStage
from anthroforge.core.skin_fitting import Settings
from anthroforge.native.mesh import NativeCancellation
from tests.test_shortcut_attachment_edits import retained_anchor
from tests.test_shortcut_explicit_scope import driver
from tests.test_skin_reference import build


def reference(session, bone):
    mesh = session.document.entity(bone).result.asset
    data = skin_assets.create({}, {})
    session.resources.skin[data.digest] = data
    skin = session.document.skin
    session.replace_document(
        skin=replace(
            skin,
            topology=SkinStage(asset=mesh, data=data.digest),
            deformation_settings=replace(skin.deformation_settings, proxy_resolution=8),
        )
    )
    build(session)


def configured(session, root, child):
    identity = driver(session, root, child)
    policy = dict(scope=root, descendants=[dict(target=child, follow_rotation="DISABLED")])
    session.command("driver.configure", driver=identity, changes=dict(policy=policy))
    reference(session, root)
    return identity


def test_driver_attachment_policy_sampling_matches_explicit_edit(session, assembly):
    root, child = assembly
    identity = configured(session, root, child)
    before = session.document
    token, settings = NativeCancellation(session.engine), Settings(0, 0.1, samples=5)
    arrays, error = skin_fit_capture.capture(
        before, session.resources, session.preferences.value, identity, settings, token
    )
    assert session.document is before and error < 1e-6
    session.command("driver.value", driver=identity, value=0.1)
    session.wait()
    current = session.assets[session.document.skin.final.asset].mesh.array(0)
    np.testing.assert_allclose(arrays["targets"][-1], current, atol=1e-7)
    assert session.document.entity(child).attachment == before.entity(child).attachment
    assert session.document.entity(child).pose_receipt.effective.follow_rotation is False


def test_owner_backsolve_is_used_during_skin_sampling(session, assembly):
    root, child = assembly
    identity, ref = backsolve(session, child)
    reference(session, root)
    anchor, before = retained_anchor(session, child), session.document
    settings, token = Settings(1, 1.1, samples=5), NativeCancellation(session.engine)
    arrays, _ = skin_fit_capture.capture(
        before, session.resources, session.preferences.value, identity, settings, token
    )
    assert session.document is before
    session.command("shortcut.set", reference=ref, value=1.1)
    session.wait()
    assert retained_anchor(session, child) == pytest.approx(anchor)
    current = session.assets[session.document.skin.final.asset].mesh.array(0)
    np.testing.assert_allclose(arrays["targets"][-1], current, atol=1e-7)


def backsolve(session, child):
    ref = dict(target=child, path=["transform", "scale"], component=0)
    identity = session.command("shortcut.expose", reference=ref)
    session.command("shortcut.configure", reference=ref, policy=dict(backsolve=True))
    return identity, ref
