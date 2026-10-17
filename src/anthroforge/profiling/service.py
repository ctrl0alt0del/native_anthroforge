"""One explicit recording lifecycle, independently owned by the application session."""

from collections import Counter
from collections.abc import Callable
from threading import Event, RLock, Thread, get_native_id
from time import perf_counter_ns
from typing import Any
from uuid import uuid4

from . import lifecycle
from .buffer import EventBuffer
from .native_calls import NativeCalls
from .spans import Spans


class RuntimeProfiler:
    def __init__(self) -> None:
        self.active, self.state, self.generation = False, "idle", 0
        self.collector, self.buffer, self.worker = None, None, None
        self.spans, self.native = Spans(self), NativeCalls(self)
        self.stop_event, self.done = Event(), Event()
        self.losses, self.collector_status = Counter(), {}
        self.recording_id, self.path, self.error = "", "", ""
        self.started_ns = self.stopped_ns = self.record_cost_ns = self.drain_cost_ns = 0
        self.memory_limit, self.seconds = 128 * 1024 * 1024, 120
        self.manifest = {}
        self.lock = RLock()

    def start(self, seconds=120, memory_mib=128):
        lifecycle.validate_start(self, seconds, memory_mib)
        self.seconds, self.memory_limit = seconds, int(memory_mib * 1024 * 1024)
        self.recording_id, self.generation = str(uuid4()), self.generation + 1
        self.buffer = EventBuffer(seconds, self.memory_limit - lifecycle.reserve(self))
        self.losses, self.collector_status = Counter(), {}
        self.path, self.error, self.record_cost_ns, self.drain_cost_ns = "", "", 0, 0
        self.stop_event.clear()
        self.done.clear()
        self.started_ns, self.stopped_ns = perf_counter_ns(), 0
        lifecycle.start_collectors(self)
        return self.status()

    def stop(self, path=None, wait=False):
        lifecycle.request_stop(self, path)
        if wait:
            self.done.wait()
            if self.error:
                raise OSError(self.error)
        return self.status()

    def status(self):
        return dict(
            state=self.state,
            recording=self.active,
            recording_id=self.recording_id,
            path=self.path,
            error=self.error,
            losses=dict(self.losses),
            storage=self.buffer.describe() if self.buffer else {},
            collector=dict(self.collector_status),
        )

    def operation(self, name: str, arguments: dict[str, Any]) -> Any:
        operations = {
            "profile.start": self.start,
            "profile.stop": self.stop,
            "profile.status": self.status,
        }
        if name not in operations:
            raise ValueError("Unknown profiling operation: " + name)
        return operations[name](**arguments)

    def call(
        self,
        category: str,
        name: str,
        function: Callable,
        *args: Any,
        _metadata: dict | None = None,
        **kwargs: Any,
    ) -> Any:
        if not self.active:
            return function(*args, **kwargs)
        return self.measured_call(category, name, function, args, kwargs, _metadata)

    def measured_call(self, category, name, function, args, kwargs, metadata):
        with self.lock:
            token = self.spans.begin(category, name, metadata) if self.active else None
        try:
            return function(*args, **kwargs)
        finally:
            with self.lock:
                self.spans.finish(token)

    def record(self, event):
        with self.lock:
            if self.state in ("recording", "stopping"):
                self.append(event)

    def append(self, event):
        if self.buffer is None:
            return
        start = perf_counter_ns()
        try:
            self.buffer.append(event)
        except (ValueError, TypeError, OverflowError):
            self.losses["invalid_event"] += 1
        self.record_cost_ns += perf_counter_ns() - start

    def event(self, category, name, **metadata):
        if self.active:
            self.record(
                dict(
                    cat=category,
                    name=name,
                    ph="i",
                    s="t",
                    pid=1,
                    tid=get_native_id(),
                    ts=perf_counter_ns() / 1000,
                    args=metadata,
                )
            )

    def launch_worker(self):
        self.worker = Thread(
            target=lifecycle.collect_and_export,
            args=(self,),
            name="anthroforge-profile-export",
            daemon=True,
        )
        self.worker.start()

    def close(self) -> None:
        if self.state == "recording":
            self.stop()
        if self.worker:
            self.worker.join(timeout=4)
        self.native.stop()
