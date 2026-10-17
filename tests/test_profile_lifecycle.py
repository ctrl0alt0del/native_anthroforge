import json
import subprocess
import sys
from threading import Event
from time import sleep
from zipfile import ZipFile

from anthroforge.application.session import Session
from anthroforge.core.jobs import Job
from anthroforge.profiling import RuntimeProfiler


def events(path):
    with ZipFile(path) as archive:
        return json.loads(archive.read("trace.json"))["traceEvents"]


def test_running_and_queued_jobs_are_reported_without_changing_checkpoint(session, tmp_path):
    first, second, jobs = queued_pair(session)
    before = session.scheduler.checkpoint
    session.command("profile.start")
    session.command("profile.stop", path=str(tmp_path / "jobs.zip"), wait=True)
    assert session.scheduler.checkpoint is before and session.scheduler.blocked
    captured = events(tmp_path / "jobs.zip")
    assert {
        e["args"]["job"] for e in captured if e["name"] == "active_at_start" and "job" in e["args"]
    } == {j.id for j in jobs}
    first.set()
    second.set()


def test_cancellation_keeps_lifecycle_identity(session, tmp_path):
    gate, published = Event(), []
    session.command("profile.start")
    job = controlled("obsolete", "surface", gate, published)
    session.scheduler.submit(job)
    session.scheduler.tick()
    session.scheduler.invalidate({"surface"})
    gate.set()
    session.scheduler.wait(timeout=3)
    session.command("profile.stop", path=str(tmp_path / "cancel.zip"), wait=True)
    states = {e["name"] for e in events(tmp_path / "cancel.zip") if e["args"].get("job") == job.id}
    assert {"queued", "cancel_requested", "obsolete"} <= states
    assert not published and not session.scheduler.blocked


def controlled(label, output, gate, published):
    return Job(
        label,
        frozenset((output,)),
        lambda doc: doc,
        lambda doc, cancel: gate.wait(3),
        published.append,
    )


def queued_pair(session):
    first, second, published = Event(), Event(), []
    jobs = [
        controlled("first", "shared", first, published),
        controlled("second", "shared", second, published),
    ]
    for job in jobs:
        session.scheduler.submit(job)
    session.scheduler.tick()
    return first, second, jobs


class BrokenCollector:
    def start(self):
        pass

    def stop(self):
        pass

    def drain(self):
        raise ConnectionError("fixture collector failed")


def test_collector_failure_keeps_application_capture_and_reports_missing_data(tmp_path):
    profiler = RuntimeProfiler()
    profiler.collector = BrokenCollector()
    profiler.start()
    sleep(0.15)
    assert profiler.active
    profiler.call("test", "continues", sum, [1, 2])
    profiler.stop(tmp_path / "partial.zip", wait=True)
    with ZipFile(tmp_path / "partial.zip") as archive:
        manifest = json.loads(archive.read("manifest.json"))
    assert not manifest["complete"] and manifest["losses"]["collector_failure"] == 1
    assert any(e["name"] == "continues" for e in events(tmp_path / "partial.zip"))


def test_native_hooks_are_removed_and_second_capture_still_works(session, tmp_path):
    session.command("primitive.create", kind="BODY")
    session.wait()
    original = session.engine.library.af_transform
    for index in range(2):
        session.command("profile.start")
        assert session.engine.library.af_transform is not original
        session.engine.transform([0, 0, 0, 0, 0, 0, 1, 1, 1])
        session.command("profile.stop", path=str(tmp_path / f"{index}.zip"), wait=True)
        assert session.engine.library.af_transform is original
        assert any(e["name"] == "af_transform" for e in events(tmp_path / f"{index}.zip"))


def test_headless_profiler_does_not_import_qt(tmp_path):
    script = (
        "import sys; from anthroforge.application.session import Session; "
        "s=Session(); s.command('profile.start'); "
        "s.command('primitive.create',kind='BODY'); s.command('wait'); "
        "s.command('profile.stop',path=sys.argv[1],wait=True); s.close(); "
        "assert not any(m.startswith(('PySide6','shiboken6')) for m in sys.modules)"
    )
    subprocess.run([sys.executable, "-c", script, str(tmp_path / "headless.zip")], check=True)


def test_borrowed_profiler_survives_session_close_and_observes_replacement(tmp_path):
    profiler = RuntimeProfiler()
    profiler.start()
    for _ in range(2):
        session = Session(profiler=profiler)
        session.command("primitive.create", kind="BODY")
        session.wait()
        session.close()
        assert profiler.active and not profiler.native.originals
    profiler.stop(tmp_path / "replaced.zip", wait=True)
    captured = events(tmp_path / "replaced.zip")
    commands = [e for e in captured if e["cat"] == "command" and e["name"] == "primitive.create"]
    assert len({e["args"]["document"] for e in commands}) == 2
    assert len([e for e in captured if e["name"] == "af_body_base_geometry"]) == 2


def test_open_keeps_profiler_on_replacement_scheduler(session, tmp_path):
    path = str(tmp_path / "saved.anthroforge")
    session.command("save", path=path, blocked_policy="wait")
    session.command("profile.start")
    session.command("open", path=path)
    session.command("primitive.create", kind="BODY")
    session.wait()
    session.command("profile.stop", path=str(tmp_path / "opened.zip"), wait=True)
    states = {e["name"] for e in events(tmp_path / "opened.zip") if e["cat"] == "task.lifecycle"}
    assert {"queued", "succeeded"} <= states
