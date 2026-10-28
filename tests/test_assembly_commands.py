from tests.test_assembly_resources import prepare_source


def prepared(session, tmp_path):
    curve, path, _ = prepare_source(session, tmp_path)
    inspected = session.command("assembly.inspect", path=str(path))
    session.wait()
    result = session.command("assembly.prepare", source=inspected["source"], selected=[curve.id])
    session.wait()
    assert session.command("assembly.status")["ready"]
    return curve, result["token"]


def test_headless_commands_copy_without_adopting_source_or_startup_jobs(session, tmp_path):
    before = session.document.id
    curve, token = prepared(session, tmp_path)
    result = session.command("assembly.import", token=token)
    assert session.document.id == before
    assert session.document.object(result["identities"][curve.id]).name == curve.name
    assert all(not j.writes for j in session.scheduler.jobs)
    assert session.command("assembly.status")["source_state"] == "idle"


def test_unrelated_destination_edit_does_not_discard_construction_import(session, tmp_path):
    _, token = prepared(session, tmp_path)
    session.replace_document(name="Unrelated rename")
    session.command("assembly.import", token=token)
    assert session.document.name == "Unrelated rename"


def test_cancelled_candidate_cannot_publish_partial_graph(session, tmp_path):
    _, token = prepared(session, tmp_path)
    before = session.document
    session.command("assembly.cancel")
    session.wait()
    assert session.document is before
    assert session.assembly.preparation.candidate is None
