"""Summarize cache events; overlapping misses are candidates, not inferred saved time."""

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from zipfile import ZipFile


def capture(path):
    with ZipFile(path) as archive:
        trace = json.loads(archive.read("trace.json"))
        manifest = json.loads(archive.read("manifest.json"))
        summary = json.loads(archive.read("summary.json"))
    return trace["traceEvents"], manifest, summary


def cache_events(events):
    return sorted((e for e in events if e.get("cat") == "cache"), key=lambda e: e["ts"])


def observe(event, state, overlaps):
    data, action = event["args"], event["name"]
    key = (data["cache"], data.get("key", ""))
    if action == "miss":
        if key in state and actor(state[key]) != actor(event):
            overlaps.append(dict(first=state[key], second=event))
        state[key] = event
    elif action in ("insert", "bypass", "reuse", "lease"):
        state.pop(key, None)
    elif action == "clear":
        for candidate in tuple(state):
            if candidate[0] == key[0]:
                del state[candidate]


def actor(event):
    return event.get("tid"), event["args"].get("job", "")


class Summary:
    def __init__(self):
        self.counts, self.keys = defaultdict(Counter), defaultdict(set)
        self.overlaps, self.files, self.native = [], [], Counter()
        self.state, self.evicted, self.rebuilt = {}, set(), Counter()

    def ingest(self, path):
        events, manifest, summary = capture(path)
        self.files.append(
            dict(path=str(path), complete=manifest["complete"], storage=manifest["storage"])
        )
        for event in cache_events(events):
            track(event, self.counts, self.keys, self.evicted, self.rebuilt)
            observe(event, self.state, self.overlaps)
        self.native.update(
            {
                k: v["inclusive_total_us"]
                for k, v in summary["durations"].items()
                if k.startswith("native/")
            }
        )

    def result(self):
        return dict(
            counts=self.counts,
            distinct_keys={k: len(v) for k, v in self.keys.items()},
            overlapping_misses=self.overlaps,
            rebuilt_evicted_keys=self.rebuilt,
            files=self.files,
            native_us=self.native,
        )


def summarize(paths):
    summary = Summary()
    for path in paths:
        summary.ingest(path)
    return summary.result()


def track(event, counts, keys, evicted, rebuilt):
    data, action = event["args"], event["name"]
    name, key = data["cache"], (data["cache"], data.get("key", ""))
    counts[name][action] += 1
    if action == "evict":
        counts[name]["evict_" + data["reason"]] += 1
        evicted.add(key)
    if action == "miss":
        keys[name].add(key)
        rebuilt[name] += key in evicted


if __name__ == "__main__":
    folder = Path(sys.argv[1])
    result = summarize(sorted(folder.glob("edit-*.afprofile.zip")))
    (folder / "cache-summary.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k not in ("files", "native_us")}))
