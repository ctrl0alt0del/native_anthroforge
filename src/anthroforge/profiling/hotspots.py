"""Bounded individual slow spans, preserving IDs for machine-readable attribution."""

from heapq import heappush, heappushpop

CATEGORIES = frozenset(("input", "qml.binding", "task", "native", "ui", "profiler"))


class Hotspots:
    def __init__(self):
        self.groups, self.serial = {}, 0

    def observe(self, event):
        if event["cat"] not in CATEGORIES:
            return
        self.serial += 1
        group = self.groups.setdefault(event["cat"], [])
        item = event["dur"], self.serial, event
        (heappush if len(group) < 10 else heappushpop)(group, item)

    def report(self):
        return {
            key: [item[2] for item in sorted(items, reverse=True)]
            for key, items in self.groups.items()
        }
