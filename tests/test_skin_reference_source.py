"""The simulation proxy follows the addon draft source without replacing final topology."""

import json
from dataclasses import replace
from types import SimpleNamespace

import numpy as np
import pytest

from anthroforge.application import skin_inputs
from anthroforge.application import skin_reference_evaluation as reference
from anthroforge.core.results import Port
from anthroforge.native import skin_proxy
from tests.test_skin_reference import build, topology
from tools.check_skin_assembly import quads


def test_reference_uses_existing_envelope_and_declares_its_revision(session):
    topology(session)
    skin = session.document.skin
    session.replace_document(skin=replace(skin, envelope=skin.topology))
    before = session.assets[skin.topology.asset].mesh
    accepted = build(session)
    metadata = json.loads(session.resources.skin[accepted.reference].metadata)
    assert metadata["proxy"]["source"] == "draft_envelope"
    assert Port(str(session.document.id), "skin_envelope") in skin_inputs.reference_build(
        session.document
    )
    np.testing.assert_array_equal(
        session.assets[accepted.final.asset].mesh.array(0), before.array(0)
    )
    assert any(read.output == "skin_envelope" for read in accepted.final.inputs)


def test_combined_build_uses_fresh_envelope_and_fallback_is_explicit(session):
    topology(session)
    skin = session.document.skin
    target = session.assets[skin.topology.asset].mesh
    fresh = object()
    assert reference.proxy_source(session.document, session.resources, target, fresh) == (
        fresh,
        "draft_envelope",
    )
    assert reference.proxy_source(session.document, session.resources, target, None) == (
        target,
        "topology_fallback",
    )


def test_missing_envelope_is_not_silently_replaced_by_topology(session):
    missing = SimpleNamespace(skin=SimpleNamespace(envelope=SimpleNamespace(asset="missing")))
    # A missing retained resource is a failure, not permission to change the reference source.
    with pytest.raises(KeyError):
        reference.proxy_source(missing, session.resources, object(), None)


def test_reference_below_target_preserves_blender_float_coordinates(session):
    points = np.array([[0.123456789, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]])
    mesh = quads(session.engine, points, [[0, 1, 2, 3]])
    result = skin_proxy.reference(mesh)
    np.testing.assert_array_equal(result.array(0), points.astype(np.float32).astype(np.float64))
    np.testing.assert_array_equal(mesh.array(0), points)
