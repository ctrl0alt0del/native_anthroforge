from dataclasses import replace

from anthroforge.application.session import Session


def test_change_descriptions_follow_edits_publication_and_undo():
    session = Session()
    root = session.command("scp.empty", name="Root")
    cursor = session.changes.serial
    session.begin()
    session.command("scp.rename", entity=root, name="Renamed")
    session.commit()
    assert session.changes.since(cursor).entities[root] >= {"name"}
    cursor = session.changes.serial
    session.navigate(-1)
    assert "name" in session.changes.since(cursor).entities[root]
    assert session.document.entity(root).name == "Root"
    session.close()


def test_change_journal_is_bounded_and_marks_missed_changes_for_rebuild():
    session = Session()
    for revision in range(100):
        session.document = replace(session.document, revision=revision)
    assert len(session.changes.records) == 64
    assert session.changes.since(0).reset
    assert not session.changes.since(session.changes.serial).reset
    session.close()
