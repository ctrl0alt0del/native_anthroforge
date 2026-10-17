"""Synchronous wall/CPU spans and explicit per-thread correlation context."""

import json
from collections.abc import Callable
from functools import wraps
from threading import get_native_id, local
from time import perf_counter_ns, thread_time_ns
from typing import Any, TypeVar, cast

F = TypeVar("F", bound=Callable[..., Any])


class Spans:
    def __init__(self, profiler):
        self.profiler, self.local = profiler, local()
        self.pending, self.serial = {}, 0
        self.bytes = self.observation_cost_ns = 0

    def measure(self, function, *args):
        start = perf_counter_ns()
        try:
            return function(*args)
        finally:
            self.observation_cost_ns += perf_counter_ns() - start

    def begin(self, category, name, metadata):
        self.serial += 1
        key, parent = self.serial, self.parent()
        item = make_span(category, name, dict(metadata or {}, span=key, parent=parent))
        if not self.retain(key, item):
            return None
        self.local.current = key
        return key, parent, thread_time_ns(), self.profiler.generation

    def retain(self, key, item):
        payload = json.dumps(item, separators=(",", ":"), allow_nan=False).encode()
        size = len(payload) + 128
        if size > 16384 or self.bytes + size > 512 * 1024 or len(self.pending) >= 4096:
            self.profiler.losses["span_capacity"] += 1
            return False
        self.pending[key] = payload
        self.bytes += size
        return True

    def parent(self):
        if getattr(self.local, "generation", -1) != self.profiler.generation:
            self.local.current, self.local.generation = 0, self.profiler.generation
        return getattr(self.local, "current", 0)

    def finish(self, token):
        if token is None:
            return
        key, parent, cpu, generation = token
        if generation != self.profiler.generation:
            return
        self.local.current = parent
        item = self.release(key)
        if item is not None and self.profiler.active:
            item["dur"] = perf_counter_ns() / 1000 - item["ts"]
            item["args"]["thread_cpu_us"] = (thread_time_ns() - cpu) / 1000
            self.profiler.record(item)

    def release(self, key):
        payload = self.pending.pop(key, None)
        if payload is not None:
            self.bytes -= len(payload) + 128
            return json.loads(payload)
        return None

    def freeze(self, timestamp):
        while self.pending:
            item = self.release(next(iter(self.pending)))
            item = dict(item, dur=max(0, timestamp - item["ts"]))
            item["args"] = dict(item["args"], truncated_end=True)
            self.profiler.record(item)


def make_span(category, name, metadata):
    return dict(
        cat=category,
        name=name,
        ph="X",
        pid=1,
        tid=get_native_id(),
        ts=perf_counter_ns() / 1000,
        args=metadata,
    )


def measured(category: str, lookup: Callable[[Any], Any]) -> Callable[[F], F]:
    def decorate(function: F) -> F:
        @wraps(function)
        def invoke(owner, *args, **kwargs):
            profiler = lookup(owner)
            if profiler is None or not profiler.active:
                return function(owner, *args, **kwargs)
            return profiler.call(category, function.__qualname__, function, owner, *args, **kwargs)

        return cast(F, invoke)

    return decorate
