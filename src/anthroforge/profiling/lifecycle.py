"""Collector start/stop and export failure handling; no dependency on the document."""

from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter_ns

from . import report

LIMITATIONS = [
    "No Python/C++ stack samples or GPU execution timings",
    "Frame submission is not physical display presentation",
    "Observer effects cannot be exactly subtracted from durations",
    "Qt owns transient producer buffers outside the retention ring",
    "Collector timers cover measured boundaries, not every Qt producer hook or CPU cache effect",
    "Input dispatch duration is measured; OS queue wait and physical input latency are unavailable",
]


def reserve(profiler):
    return (32 if profiler.collector else 8) * 1024 * 1024


def validate_start(profiler, seconds, memory_mib):
    if profiler.state in ("recording", "stopping", "exporting", "export_failed"):
        raise ValueError("Finish or retry the current performance capture first")
    minimum = 64 if profiler.collector else 16
    if not 1 <= seconds <= 3600 or not minimum <= memory_mib <= 1024:
        raise ValueError(f"Recording requires 1–3600 seconds and {minimum}–1024 MiB")


def start_collectors(profiler):
    try:
        if profiler.collector:
            profiler.collector.start()
        profiler.active, profiler.state = True, "recording"
        profiler.native.start()
        profiler.launch_worker()
    except Exception:
        profiler.active, profiler.state = False, "idle"
        profiler.native.stop()
        stop_collector(profiler)
        profiler.done.set()
        raise


def request_stop(profiler, path):
    if profiler.state == "export_failed":
        retry_export(profiler, path)
        return
    if profiler.state != "recording":
        raise ValueError("No performance recording is active")
    profiler.path = str(path or default_path(profiler))
    freeze_application(profiler)
    profiler.native.stop()
    stop_collector(profiler)
    profiler.stop_event.set()


def retry_export(profiler, path):
    profiler.error, profiler.path = "", str(path or profiler.path)
    profiler.done.clear()
    profiler.launch_worker()


def freeze_application(profiler):
    with profiler.lock:
        profiler.stopped_ns = perf_counter_ns()
        profiler.active, profiler.state = False, "stopping"
        profiler.spans.freeze(profiler.stopped_ns / 1000)


def default_path(profiler):
    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    return report.default_directory() / f"{stamp}-{profiler.recording_id[:8]}.afprofile.zip"


def drain(profiler):
    if profiler.collector is None or profiler.collector_disabled:
        return
    start = perf_counter_ns()
    for _ in range(16):
        for event in profiler.collector.drain():
            profiler.record(event)
        profiler.collector_status = profiler.collector.status()
        if not profiler.collector_status.get("queued_bytes"):
            break
    profiler.drain_cost_ns += perf_counter_ns() - start


def collect_and_export(profiler):
    try:
        while not profiler.stop_event.wait(0.1):
            poll_collector(profiler)
        finish_collector(profiler)
        with profiler.lock:
            profiler.state = "exporting"
        profiler.manifest = manifest(profiler)
        report.write_bundle(Path(profiler.path), profiler.buffer, profiler.manifest)
        profiler.state, profiler.buffer = "saved", None
    except Exception as error:
        profiler.error, profiler.state = str(error), "export_failed"
    finally:
        profiler.done.set()


def finish_collector(profiler):
    deadline = perf_counter_ns() + 2_000_000_000
    while profiler.collector and not profiler.collector_disabled:
        poll_collector(profiler)
        state = profiler.collector_status
        if state.get("finished") and not state.get("queued_bytes"):
            break
        if perf_counter_ns() >= deadline:
            profiler.losses["collector_stop_timeout"] += 1
            break
        profiler.done.wait(0.01)


def poll_collector(profiler):
    try:
        drain(profiler)
    except Exception as error:
        profiler.collector_disabled = True
        profiler.collector_status = dict(failure=type(error).__name__, finished=True)
        profiler.losses["collector_failure"] += 1


def stop_collector(profiler):
    try:
        if profiler.collector:
            profiler.collector.stop()
    except Exception as error:
        profiler.collector_disabled = True
        profiler.collector_status = dict(failure=type(error).__name__, finished=True)
        profiler.losses["collector_stop_failure"] += 1


def manifest(profiler):
    return dict(
        schema_version=1,
        recording_id=profiler.recording_id,
        environment=report.environment(),
        clock="monotonic perf_counter, microseconds",
        storage=storage(profiler),
        requested_interval_ns=[profiler.started_ns, profiler.stopped_ns],
        complete=complete(profiler),
        capabilities=capabilities(profiler),
        profiler=costs(profiler),
        losses=dict(profiler.losses),
        qt=profiler.collector_status,
        limitations=LIMITATIONS,
    )


def storage(profiler):
    return dict(
        profiler.buffer.describe(),
        owned_budget_bytes=profiler.memory_limit,
        reserved_bytes=reserve(profiler),
    )


def complete(profiler):
    state = profiler.collector_status
    return not (
        profiler.losses
        or state.get("failure")
        or state.get("dropped")
        or profiler.buffer.oversized
        or state.get("model_watch_skipped")
    )


def capabilities(profiler):
    return dict(
        commands=True,
        tasks=True,
        native_calls=True,
        qml=profiler.collector is not None,
        input=profiler.collector is not None,
        frames=profiler.collector is not None,
        model_changes=profiler.collector is not None,
        stack_sampling=False,
    )


def costs(profiler):
    return dict(
        record_wall_ns=profiler.record_cost_ns,
        drain_inclusive_wall_ns=profiler.drain_cost_ns,
        qt_encode_wall_ns=profiler.collector_status.get("encode_ns", 0),
        qt_decode_inclusive_wall_ns=profiler.collector_status.get("decode_inclusive_ns", 0),
        qt_decode_thread_cpu_ns=profiler.collector_status.get("decode_cpu_ns", 0),
        note="Measured collector wall time can overlap; export is measured separately.",
    )
