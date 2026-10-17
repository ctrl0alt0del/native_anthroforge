"""Synchronous wall/CPU spans and explicit per-thread correlation context."""

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

    def begin(self, category, name, metadata):
        self.serial += 1
        key, parent = self.serial, self.parent()
        item = make_span(category, name, dict(metadata or {}, span=key, parent=parent))
        if len(self.pending) >= 4096:
            self.profiler.losses["span_capacity"] += 1
            return None
        self.pending[key] = item
        self.local.current = key
        return key, parent, thread_time_ns(), self.profiler.generation

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
        item = self.pending.pop(key, None)
        if item is not None and self.profiler.active:
            item["dur"] = perf_counter_ns() / 1000 - item["ts"]
            item["args"]["thread_cpu_us"] = (thread_time_ns() - cpu) / 1000
            self.profiler.record(item)

    def freeze(self, timestamp):
        for item in list(self.pending.values()):
            item = dict(item, dur=max(0, timestamp - item["ts"]))
            item["args"] = dict(item["args"], truncated_end=True)
            self.profiler.record(item)
        self.pending.clear()


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
