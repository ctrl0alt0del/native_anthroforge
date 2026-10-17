import json
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from zipfile import ZipFile

import pytest

from anthroforge.profiling import RuntimeProfiler
from anthroforge.profiling.buffer import EventBuffer


def bundle(path):
    with ZipFile(path) as archive:
        return {name: json.loads(archive.read(name)) for name in archive.namelist()}


def event(stamp, duration=0):
    return dict(ts=stamp, dur=duration, cat="test", name="work", ph="X", pid=1, tid=1, args={})


def test_ring_evicts_oldest_and_clips_spans():
    buffer = EventBuffer(seconds=1, byte_limit=2000)
    buffer.append(event(0, 20))
    buffer.append(event(400_000, 1_000_000))
    buffer.append(event(1_800_000))
    events = list(buffer.events())
    assert buffer.evicted == 1
    assert events[0]["ts"] == 800_000
    assert events[0]["dur"] == 600_000
    assert events[0]["args"]["truncated_start"]


def test_ring_bounds_bytes_and_rejects_oversized_events():
    buffer = EventBuffer(byte_limit=1000)
    for i in range(100):
        buffer.append(event(i))
    buffer.append(dict(event(101), args={"large": "x" * 2000}))
    assert buffer.bytes <= 1000 and buffer.evicted > 0
    assert buffer.oversized == 1


def test_disabled_profiler_does_not_collect_or_create_worker():
    profiler = RuntimeProfiler()
    assert profiler.call("test", "sum", sum, [1, 2]) == 3
    assert profiler.worker is None and profiler.buffer is None
    assert not profiler.spans.pending


def test_recording_is_not_a_document_edit_or_calculation(session, tmp_path):
    before, history = session.document, len(session.history.entries)
    session.command("profile.start", memory_mib=2)
    assert session.document is before and not session.scheduler.blocked
    session.command("inspect")
    result = session.command("profile.stop", path=str(tmp_path / "report.zip"), wait=True)
    assert result["state"] == "saved"
    assert session.document is before and len(session.history.entries) == history
    report = bundle(result["path"])
    assert report["manifest.json"]["schema_version"] == 1
    assert not report["manifest.json"]["capabilities"]["qml"]
    assert "command/inspect" in report["summary.json"]["durations"]


def test_capture_native_and_task_stages(session, tmp_path):
    session.command("profile.start", memory_mib=4)
    session.command("primitive.create", kind="BODY")
    session.command("wait", timeout=5)
    path = tmp_path / "body.zip"
    session.command("profile.stop", path=str(path), wait=True)
    events = bundle(path)["trace.json"]["traceEvents"]
    assert {"prepare", "execute", "publish"} <= {e["name"] for e in events if e["cat"] == "task"}
    assert any(e["cat"] == "native" for e in events)
    assert any(e["name"] == "succeeded" for e in events)
    assert not session.profiler.native.originals


def test_export_failure_keeps_capture_for_retry(tmp_path):
    profiler = RuntimeProfiler()
    profiler.start(memory_mib=2)
    profiler.call("test", "sum", sum, [1, 2])
    blocked = tmp_path / "blocked"
    blocked.write_text("file, not directory")
    with pytest.raises(OSError):
        profiler.stop(blocked / "report.zip", wait=True)
    assert profiler.state == "export_failed" and profiler.buffer is not None
    result = profiler.stop(tmp_path / "recovered.zip", wait=True)
    assert result["state"] == "saved"
    assert bundle(result["path"])["summary.json"]["durations"]["test/sum"]["count"] == 1


def test_repeated_recordings_do_not_retain_previous_events(tmp_path):
    profiler = RuntimeProfiler()
    for name in ("first", "second"):
        profiler.start(memory_mib=2)
        profiler.call("test", name, sum, [1])
        profiler.stop(tmp_path / f"{name}.zip", wait=True)
    data = bundle(tmp_path / "second.zip")["summary.json"]["durations"]
    assert "test/first" not in data and "test/second" in data


def test_recording_lifecycle_rejects_overlapping_start(tmp_path):
    profiler = RuntimeProfiler()
    with pytest.raises(ValueError):
        profiler.stop()
    profiler.start(memory_mib=2)
    with pytest.raises(ValueError):
        profiler.start()
    profiler.stop(tmp_path / "done.zip", wait=True)


def test_stop_marks_running_span_and_late_return_does_not_change_report(tmp_path):
    profiler, entered, release = RuntimeProfiler(), Event(), Event()
    profiler.start(memory_mib=2)
    with ThreadPoolExecutor() as pool:
        work = pool.submit(profiler.call, "test", "waiting", blocking, entered, release)
        assert entered.wait(2)
        path = tmp_path / "partial.zip"
        profiler.stop(path, wait=True)
        release.set()
        work.result(timeout=2)
    events = bundle(path)["trace.json"]["traceEvents"]
    assert len(events) == 1 and events[0]["args"]["truncated_end"]


def blocking(entered, release):
    entered.set()
    assert release.wait(5)
