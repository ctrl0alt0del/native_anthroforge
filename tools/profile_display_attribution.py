"""Experiment-only boundary observation, without changing application behavior."""

from collections import defaultdict
from contextlib import ExitStack
from functools import wraps
from time import perf_counter
from unittest.mock import patch

from anthroforge.application import geometry_ownership
from anthroforge.desktop import image_scene, path_scene, scene_projection, scene_state
from anthroforge.desktop.construction_projection import ConstructionProjection

TARGETS = (
    (scene_projection.SceneProjection, "synchronize"),
    (scene_projection, "publish"),
    (ConstructionProjection, "synchronize"),
    (ConstructionProjection, "publish"),
    (scene_state, "picking_inputs"),
    (scene_state, "snapping_inputs"),
    (path_scene, "prepare_picking"),
    (image_scene, "prepare_picking"),
    (geometry_ownership, "collect"),
)


def measured(profiler, original, record):
    @wraps(original)
    def invoke(*args, **kwargs):
        start = perf_counter()
        try:
            return profiler.call("detail", original.__qualname__, original, *args, **kwargs)
        finally:
            record["calls"] += 1
            record["seconds"] += perf_counter() - start

    return invoke


def visited(original, record):
    @wraps(original)
    def invoke(owner, session, item):
        before = owner.records.get(item.id)
        result = original(owner, session, item)
        record["calls"] += 1
        record["changed"] += before is not owner.records.get(item.id)
        return result

    return invoke


class Attribution(ExitStack):
    def __init__(self, profiler):
        super().__init__()
        self.records = defaultdict(lambda: dict(calls=0, seconds=0.0))
        for owner, name in TARGETS:
            original = getattr(owner, name)
            key = owner.__name__ + "." + name
            self.enter_context(
                patch.object(owner, name, measured(profiler, original, self.records[key]))
            )
        self.observe_visits()

    def observe_visits(self):
        record = self.records["construction_visits"] = dict(calls=0, changed=0)
        original = ConstructionProjection.update_record
        self.enter_context(
            patch.object(ConstructionProjection, "update_record", visited(original, record))
        )
