"""Inspection exposes retained evidence without editing or recomputing the document."""

from anthroforge.application import storage
from tests.test_skin_reference import build, topology


def test_report_survives_reload_and_does_not_schedule(session, tmp_path):
    topology(session)
    build(session)
    before, jobs = session.document, len(session.scheduler.jobs)
    expected = session.command("skin.report")
    assert expected["final"]["report"]["intersections"]["self_intersections"] == 0
    assert session.document is before and len(session.scheduler.jobs) == jobs
    path = tmp_path / "skin.anthroforge"
    storage.atomic_save(path, session.document, session.resources)
    session.command("open", path=str(path))
    session.wait()
    assert session.command("skin.report") == expected
