from dataclasses import replace

import pytest

from anthroforge.application.storage import write_package


def replacement(session, root, tmp_path, offset=2.0):
    item = session.document.entity(root)
    translation = [offset, 0, 0] if isinstance(offset, (float, int)) else offset
    matrix = session.engine.transform([*translation, 0, 0, 0, 1, 1, 1])
    source = replace(
        session.document,
        entities=tuple(
            replace(e, matrix=matrix) if e.id == item.id else e for e in session.document.entities
        ),
    )
    path = tmp_path / "replacement.anthroforge"
    write_package(path, source, session.resources)
    return path


def prepare(session, path, matches, **options):
    session.command("skeleton_update.inspect", path=str(path))
    inventory = session.command("skeleton_update.status", wait=True)
    session.command(
        "skeleton_update.prepare", source=inventory["source"], matches=matches, **options
    )
    result = session.command("skeleton_update.status", wait=True)
    assert result["state"] == "ready", result.get("error") or result
    return result


def test_preview_is_isolated_and_apply_propagates_with_one_undo(session, assembly, tmp_path):
    root, child = assembly
    path = replacement(session, root, tmp_path)
    before = session.document
    status = prepare(session, path, {root: root})
    assert status["ready"], status
    assert session.document is before
    expected = before.entity(child).matrix[3] + 2
    session.command("skeleton_update.apply", token=status["token"])
    assert session.document.entity(root).matrix[3] == pytest.approx(2)
    assert session.document.entity(child).matrix[3] == pytest.approx(expected)
    session.command("undo")
    assert session.document.entities == before.entities
    session.command("redo")
    assert session.document.entity(child).matrix[3] == pytest.approx(expected)


def test_cancel_keeps_live_document_and_releases_candidate(session, assembly, tmp_path):
    root, _ = assembly
    before = session.document
    prepare(session, replacement(session, root, tmp_path), {root: root})
    session.command("skeleton_update.cancel")
    assert session.document is before
    assert session.skeleton_update.runtime.preparation.candidate is None
