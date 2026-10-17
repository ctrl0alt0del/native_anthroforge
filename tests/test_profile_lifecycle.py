import json
from threading import Event
from time import sleep
from zipfile import ZipFile

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
