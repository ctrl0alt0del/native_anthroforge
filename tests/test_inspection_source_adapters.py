"""Every existing candidate family can be inspected without accepting its edit."""

import json

import numpy as np

from anthroforge.application import inspection_snapshots
from tests.conftest import CUBE
from tests.test_mesh_replacement import assessment, mirrored_scene
from tests.test_skeleton_update_commands import prepare, replacement
from tests.test_tissue_preview import ready
from tests.test_tissue_retarget import assess, replacement_membrane
from tests.test_tissue_workflow import assembly as tissue_assembly


def captured(session, kind, token):
    before, cursor = session.document, session.history.cursor
    result = session.command("inspection.capture", kind=kind, token=token)
    assert session.document is before and session.history.cursor == cursor
    json.dumps(result, allow_nan=False)
    assert result["current"]
    return inspection_snapshots.selected(session, result["snapshot"])


def test_inflation_captures_only_computed_rest_with_material_baseline(session):
    _, _, target = tissue_assembly(session)
    state = ready(session, target, changes=dict(amount=0.15))
    result = captured(session, "tissue_inflation", state["token"])
    after = next(r for r in result.layers if r.side == "after")
    assert after.stage == "rest" and after.resource is session.tissue_preview.asset.mesh
    assert next(r for r in result.layers if r.side == "before").lineage


def test_replacement_captures_mirrors_with_shared_buffers(session):
    _, target = mirrored_scene(session)
    token, _ = assessment(session, target, CUBE)
    result = captured(session, "mesh_replacement", token)
    original = next(r for r in result.layers if r.subject == target and r.side == "after")
    mirrored = next(
        r for r in result.layers if r.subject.startswith("mirror/") and r.side == "after"
    )
    assert original.resource is mirrored.resource and original.frame != mirrored.frame


def test_retarget_reads_prepared_geometry_not_live_tissue(session):
    bone, _, target = tissue_assembly(session)
    token, _ = assess(session, target, replacement_membrane(session, bone))
    result = captured(session, "tissue_retarget", token)
    after = next(r for r in result.layers if r.subject == target and r.side == "after")
    candidate = session.tissue_retarget.asset
    expected = candidate.resources.meshes[candidate.objects[target].result.asset].mesh
    np.testing.assert_array_equal(after.resource.array(0), expected.array(0))


def test_skeleton_captures_changed_poses_without_applying(session, assembly, tmp_path):
    root, child = assembly
    state = prepare(session, replacement(session, root, tmp_path), {root: root})
    result = captured(session, "skeleton_update", state["token"])
    before = next(r for r in result.layers if r.subject == child and r.side == "before")
    after = next(r for r in result.layers if r.subject == child and r.side == "after")
    assert before.frame != after.frame


def test_fitted_playback_exposes_exact_token_and_geometry(session):
    from tests.test_skin_fit_jobs import fit, setup

    item = fit(session, setup(session))
    session.command("skin.fit.preview", identity=item.id, value=0.05)
    session.wait()
    status = session.command("skin.fit.preview.status")
    result = captured(session, "skin_fit", status["token"])
    assert result.layers[-1].resource is session.skin_fit_preview.asset.mesh


def test_variant_review_uses_candidate_not_active_scene(session, assembly):
    from tests.test_variant_review import review
    from tests.test_variants import rename_bone, variant

    _, child = assembly
    key = variant(session, child)
    rename_bone(session, child, "Alternative")
    session.command("variant.leave")
    status = review(session, key)
    result = captured(session, "variant_review", status["token"])
    assert result.kind == "variant_review"
