"""Candidates are transient, reject changed inputs and commit one source-independent graph."""

import gc
import weakref

import pytest

from anthroforge.application import candidate_outputs
from anthroforge.core.jobs import ObsoleteInputs
from tests.test_skeleton_update_commands import prepare, replacement
from tests.test_skeleton_update_controls import apply
from tests.test_tissue_workflow import assembly as tissue_assembly


def test_unrelated_edit_survives_but_affected_change_stales_candidate(session, assembly, tmp_path):
    root, _ = assembly
    state = prepare(session, replacement(session, root, tmp_path), {root: root})
    point = session.command("construction.point.create", position=[5, 6, 7])
    assert session.command("skeleton_update.status")["ready"]
    apply(session, state)
    assert session.document.object(point).position == (5, 6, 7)
    state = prepare(session, replacement(session, root, tmp_path), {root: root})
    session.command("scp.transform", entity=root, values=[1, 0, 0, 0, 0, 0, 1, 1, 1])
    session.wait()
    assert session.command("skeleton_update.status")["state"] == "stale"
    with pytest.raises((ObsoleteInputs, ValueError)):
        apply(session, state)


def test_candidate_and_source_are_released_on_cancel(session, assembly, tmp_path):
    root, _ = assembly
    state = prepare(session, replacement(session, root, tmp_path), {root: root})
    candidate = weakref.ref(session.skeleton_update.ready(state["token"]))
    source = weakref.ref(session.skeleton_update.runtime.source.source)
    session.command("skeleton_update.cancel")
    gc.collect()
    assert candidate() is None and source() is None


def test_source_can_disappear_and_committed_result_roundtrips(session, assembly, tmp_path):
    root, _ = assembly
    path = replacement(session, root, tmp_path)
    state = prepare(session, path, {root: root})
    path.unlink()
    apply(session, state)
    before = session.document.entities
    saved = tmp_path / "result.anthroforge"
    session.command("save", path=str(saved), blocked_policy="wait")
    session.wait()
    session.command("open", path=str(saved))
    session.wait()
    assert session.document.entities == before


def broken_tissue(*_):
    raise ValueError("Deliberate dependent failure")


def test_new_dependent_failure_requires_exact_review_and_retains_geometry(
    session, tmp_path, monkeypatch
):
    bone, _, tissue = tissue_assembly(session)
    before = session.document.object(tissue)
    monkeypatch.setattr(candidate_outputs, "compute_tissue", broken_tissue)
    state = prepare(session, replacement(session, bone, tmp_path), {bone: bone})
    assert state["ready"], state
    findings = [r for r in state["findings"] if r["kind"] == "failure"]
    assert findings and all(r["acknowledge"] for r in findings)
    with pytest.raises(ValueError, match="Acknowledge"):
        session.command("skeleton_update.apply", token=state["token"])
    apply(session, state)
    assert session.document.object(tissue).result.asset == before.result.asset
    assert session.document.object(tissue).result.status == "failed"
