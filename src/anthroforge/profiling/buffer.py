"""Bounded immutable event storage with explicit loss and retention accounting."""

import json
from heapq import heappop, heappush
from threading import Lock


class EventBuffer:
    def __init__(self, seconds=120, byte_limit=128 * 1024 * 1024):
        self.window_us, self.limit = seconds * 1_000_000, byte_limit
        self.records, self.lock = [], Lock()
        self.bytes = self.evicted = self.oversized = self.received = 0
        self.watermark = 0.0
        self.boundary_filtered = 0

    def append(self, event):
        payload = json.dumps(event, separators=(",", ":"), allow_nan=False).encode()
        size, end = len(payload) + 256, event["ts"] + event.get("dur", 0)
        with self.lock:
            self.received += 1
            self.watermark = max(self.watermark, end)
            if size > min(self.limit, 16384):
                self.oversized += 1
                return
            heappush(self.records, (end, self.received, size, payload))
            self.bytes += size
            self.trim()

    def trim(self):
        cutoff = self.watermark - self.window_us
        while self.records and (self.bytes > self.limit or self.records[0][0] < cutoff):
            _, _, size, _ = heappop(self.records)
            self.bytes -= size
            self.evicted += 1

    def events(self):
        cutoff = self.watermark - self.window_us
        for end, _, _, payload in sorted(self.records):
            if end >= cutoff:
                yield clip_event(json.loads(payload), cutoff)

    def describe(self):
        with self.lock:
            return self.snapshot()

    def snapshot(self):
        return dict(
            received=self.received,
            retained=len(self.records),
            evicted=self.evicted,
            oversized=self.oversized,
            boundary_filtered=self.boundary_filtered,
            owned_bytes=self.bytes,
            byte_limit=self.limit,
            window_seconds=self.window_us / 1_000_000,
        )


def clip_event(event, cutoff):
    if event["ts"] < cutoff:
        event["args"] = dict(event.get("args", {}), truncated_start=True)
        if "dur" in event:
            event["dur"] -= cutoff - event["ts"]
        event["ts"] = cutoff
    return event


def capture_interval(event, start, stop):
    end = event["ts"] + event.get("dur", 0)
    if end < start or (stop and event["ts"] > stop):
        return None
    event = clip_event(event, start)
    if stop and end > stop and "dur" in event:
        event["dur"] = max(0, stop - event["ts"])
        event["args"] = dict(event.get("args", {}), truncated_end=True)
    return event
