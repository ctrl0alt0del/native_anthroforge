"""Bounded machine-readable explanations over retained trace evidence."""

from collections import Counter


class DiagnosticsSummary:
    def __init__(self):
        self.invalidations, self.cache = Counter(), Counter()
        self.memory, self.peak, self.snapshots = {}, {}, 0
        self.examples, self.latest_stamp = [], -1

    def observe(self, event):
        category, args = event["cat"], event.get("args", {})
        if category == "invalidation":
            reason = args.get("reason", event["name"])
            self.increment(self.invalidations, reason)
            if len(self.examples) < 32:
                self.examples.append(dict(time_us=event["ts"], action=event["name"], **args))
        elif category == "cache":
            self.increment(self.cache, event["name"] + ":" + args.get("reason", ""))
        elif category == "memory" and event["name"] == "geometry_snapshot":
            self.geometry(event["ts"], args)

    def increment(self, counts, key):
        key = str(key)[:128]
        counts[key if key in counts or len(counts) < 64 else "other/limit"] += 1

    def geometry(self, stamp, args):
        self.snapshots += 1
        if stamp >= self.latest_stamp:
            self.latest_stamp, self.memory = stamp, args
        values = dict(unique=args["unique_bytes"], unattributed=args["unattributed_bytes"])
        values.update({key: value["bytes"] for key, value in args["owners"].items()})
        for key, value in values.items():
            self.peak[key] = max(self.peak.get(key, 0), value)

    def report(self):
        return dict(
            invalidation_reasons=dict(self.invalidations),
            invalidation_examples=self.examples,
            cache_events=dict(self.cache),
            geometry_memory=dict(
                samples=self.snapshots, latest=self.memory, peak_observed_bytes=self.peak
            ),
            interpretation="Retained events; owners overlap; sampling can miss transient peaks.",
        )
