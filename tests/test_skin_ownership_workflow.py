"""Skin attribution follows construction bindings rather than display or parenting."""

from dataclasses import replace

import numpy as np

from anthroforge.application import skin_capture, skin_density, skin_ownership
from anthroforge.core.entities import SCP
from anthroforge.core.mirroring import MirrorRule, SharedMirrorTarget
from anthroforge.core.skin_sources import Source
from tests.test_tissue_workflow import assembly


def test_tissue_density_uses_its_fiber_supports_without_mutating_sources(session):
    bone, membrane, tissue = assembly(session)
    before = session.document
    capture = skin_capture.capture(session.engine, before, session.resources)
    mesh = session.assets[before.object(tissue).result.asset].mesh
    result = skin_density.evaluate(before, capture, mesh)
    assert not result.warnings, result.warnings
    np.testing.assert_array_equal(result.ownership.owners, result.plan.owners.index(bone))
    assert session.document is before
    assert skin_ownership.supports(before, Source(tissue, "TISSUE"), set()) == {Source(bone, "SCP")}
    assert before.object(membrane).curves


def mirrored(document):
    bone = document.entities[0]
    root = SCP("Root", id="root")
    entities = (root, replace(bone, parent=root.id))
    return replace(document, entities=entities, mirror_rules=(MirrorRule(root.id, enabled=True),))


def test_mirrored_tissue_supports_use_counterparts_and_explicit_midline_sharing(session):
    bone, membrane, tissue = assembly(session)
    document = mirrored(session.document)
    source = Source(tissue, "TISSUE", "root")
    assert skin_ownership.supports(document, source, set()) == {Source(bone, "SCP", "root")}
    fibers = [document.object(use.curve) for use in document.object(membrane).curves]
    sharing = tuple(SharedMirrorTarget(f.id, b.point) for f in fibers for b in f.bindings)
    document = replace(document, shared_mirror_targets=sharing)
    assert skin_ownership.supports(document, source, set()) == {Source(bone, "SCP")}


def test_indirect_tissue_anchor_resolves_to_skeletal_supports(session):
    bone, _, tissue = assembly(session)
    point = session.command("construction.point.create", position=[0, 0, 0.1])
    anchor = session.command("anchor.create", source=point, parent=tissue, role="TISSUE_FINAL")[
        "object_id"
    ]
    session.wait()
    child = session.command("tissue.create", source=anchor)
    session.wait()
    assert skin_ownership.supports(session.document, Source(child, "TISSUE"), set()) == {
        Source(bone, "SCP")
    }
