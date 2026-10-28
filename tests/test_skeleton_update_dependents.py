"""Reviewed previews run existing fiber and tissue algorithms, including Manual objects."""

from dataclasses import replace

import numpy as np

from tests.test_skeleton_update_commands import prepare, replacement
from tests.test_tissue_workflow import assembly, mesh


def manual(session, tissue):
    session.replace_document(
        objects=tuple(
            replace(o, update_mode="MANUAL") if o.id == tissue else o
            for o in session.document.objects
        )
    )


def test_manual_tissue_previews_and_commits_without_recalculation(session, tmp_path):
    bone, _, tissue = assembly(session)
    before = mesh(session, tissue)
    manual(session, tissue)
    state = prepare(session, replacement(session, bone, tmp_path), {bone: bone})
    assert state["ready"], state
    candidate = session.skeleton_update.ready(state["token"])
    result = candidate.document.object(tissue)
    np.testing.assert_allclose(
        candidate.resources.meshes[result.result.asset].mesh.array(0), before + [2, 0, 0], atol=1e-8
    )
    session.command("skeleton_update.apply", token=state["token"])
    session.wait()
    assert session.document.object(tissue).result == result.result
    assert session.document.object(tissue).update_mode == "MANUAL"
