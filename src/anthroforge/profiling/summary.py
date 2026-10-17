"""Bounded duration histograms; inclusive durations are never summed across sources."""

import math
from collections import Counter


class Distribution:
    def __init__(self):
        self.count, self.total, self.maximum = 0, 0.0, 0.0
        self.bins = Counter()

    def add(self, value):
        self.count += 1
        self.total += value
        self.maximum = max(self.maximum, value)
        self.bins[min(512, max(0, math.ceil(math.log2(1 + value) * 16)))] += 1

    def percentile(self, fraction):
        target, count = math.ceil(self.count * fraction), 0
        for bucket, frequency in sorted(self.bins.items()):
            count += frequency
            if count >= target:
                return 2 ** (bucket / 16) - 1
        return 0.0

    def report(self):
        return dict(
            count=self.count,
            inclusive_total_us=self.total,
            mean_us=self.total / max(1, self.count),
            max_us=self.maximum,
            p50_upper_us=self.percentile(0.5),
            p95_upper_us=self.percentile(0.95),
        )


class Summary:
    def __init__(self):
        self.durations, self.counts, self.frames = {}, Counter(), Distribution()
        self.last_frame, self.start, self.end, self.truncated = None, None, 0.0, 0

    def observe(self, event):
        key = event["cat"] + "/" + event["name"]
        if key not in self.counts and len(self.counts) >= 2048:
            key = "other/group_limit"
        self.counts[key] += 1
        self.start = min(self.start or event["ts"], event["ts"])
        self.end = max(self.end, event["ts"] + event.get("dur", 0))
        partial = any(event.get("args", {}).get(k) for k in ("truncated_start", "truncated_end"))
        self.truncated += bool(partial)
        if "dur" in event and not partial:
            self.durations.setdefault(key, Distribution()).add(event["dur"])
        if event["cat"] == "frame" and event["name"] == "submitted":
            self.frame(event["ts"])

    def frame(self, stamp):
        if self.last_frame is not None and stamp > self.last_frame:
            self.frames.add(stamp - self.last_frame)
        self.last_frame = max(stamp, self.last_frame or stamp)

    def report(self):
        durations = {key: value.report() for key, value in self.durations.items()}
        return dict(
            durations=durations,
            event_counts=dict(self.counts),
            truncated=self.truncated,
            frame_submission_intervals=self.frames.report(),
            retained_interval_us=[self.start, self.end],
            percentile_method="log2 bins, 1/16 octave",
            interpretation="Inclusive wall durations overlap; do not add categories together.",
        )
