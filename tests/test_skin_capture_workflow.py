"""The worker capture reuses accepted physical geometry and explicit source policies."""

from dataclasses import replace

import numpy as np

from anthroforge.application import skin_assets, skin_capture, skin_inputs
from anthroforge.application.construction_policy import revisions
from anthroforge.core.skin import SkinContributor
from tests.test_tissue_workflow import assembly


def test_capture_uses_final_tissues_and_records_stable_source_assets(session):
    bone, _membrane, tissue = assembly(session)
    result = skin_capture.capture(session.engine, session.document, session.resources)
    assert {row.identity.owner for row in result.sources} == {bone, tissue}
    assert all(row.asset for row in result.sources)
    assert result.geometry.vertices.shape[0] == len(result.collagen)
    assert set(result.geometry.owners) == {0, 1}
    assert result.warnings == ()


def test_capture_and_revisions_ignore_workspace_changes(session):
    bone, _membrane, _tissue = assembly(session)
    original = session.document
    inputs = skin_inputs.envelope(original)
    changed = replace(original, workspaces=(replace(original.workspaces[0], hidden=(bone,)),))
    assert revisions(original, inputs) == revisions(changed, inputs)
    first = skin_capture.capture(session.engine, original, session.resources)
    second = skin_capture.capture(session.engine, changed, session.resources)
    np.testing.assert_array_equal(first.geometry.vertices, second.geometry.vertices)
    session.command("skin.configure", section="envelope_settings", values={"gap_strength": 0.5})
    assert revisions(original, inputs) != revisions(session.document, inputs)


def test_mismatched_paint_uses_explicit_fallback_and_warning(session):
    bone, _membrane, _tissue = assembly(session)
    data = skin_assets.create({"collagen": np.zeros(2)}, {})
    session.resources.skin[data.digest] = data
    settings = SkinContributor(bone, collagen_mode="PAINTED", collagen=0.25, painted=data.digest)
    document = replace(
        session.document, skin=replace(session.document.skin, contributors=(settings,))
    )
    result = skin_capture.capture(session.engine, document, session.resources)
    assert len(result.warnings) == 1 and "uniform" in result.warnings[0]
    bone_index = next(i for i, row in enumerate(result.sources) if row.identity.owner == bone)
    start = sum(row.mesh.counts[0] for row in result.sources[:bone_index])
    count = result.sources[bone_index].mesh.counts[0]
    np.testing.assert_array_equal(result.collagen[start : start + count], 0.25)
