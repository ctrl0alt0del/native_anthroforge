"""Reusable native collision scenes preserve solver results and independent leases."""

import ctypes as c
import weakref
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace

import numpy as np

from anthroforge.native import routing, routing_scene
from anthroforge.native.mesh import INT64, NativeCancellation, pointer
from anthroforge.native.paths import Path
from tests.test_routing_surface_pins import inputs


def uncached(engine, value):
    settings = value.curve.engine_settings
    options = routing.Options(settings.samples, settings.accepted_steps, False, settings.radius)
    counters, measures = np.zeros(8, dtype=np.int64), np.zeros(8)
    handle = engine.library.af_route_path(
        *routing.arguments(routing.arrays(value)),
        c.byref(options),
        counters.ctypes.data_as(INT64),
        pointer(measures),
        0,
        0,
    )
    return Path(engine, handle)


def test_capture_reuse_matches_uncached_solver(session):
    meshes, value = inputs(session)
    reference = uncached(session.engine, value)
    events = []
    session.engine.routing_scenes.observer = lambda action, **data: events.append(action)
    for _ in range(2):
        result, _ = routing.evaluate(session.engine, value)
        np.testing.assert_allclose(result.array(), reference.array(), atol=1e-12, rtol=0)
    assert events == ["miss", "insert", "hit"]


def test_capture_keys_and_eviction_preserve_live_lease(session):
    meshes, value = inputs(session)
    engine = session.engine
    scene = routing_scene.capture(engine, routing.arrays(value), 0.002, 0)
    reference = weakref.ref(scene)
    engine.routing_scenes.capacity = 1
    changed = replace(value, matrices=tuple(reversed(value.matrices)))
    second = routing_scene.capture(engine, routing.arrays(changed), 0.002, 0)
    assert second is not scene and scene.bytes > 0
    assert engine.library.af_routing_scene_bytes(scene.handle) == scene.bytes
    del scene
    assert reference() is None
    engine.routing_scenes.clear()
    assert engine.routing_scenes.bytes == 0


def test_readonly_scene_supports_concurrent_solves_and_cancellation(session):
    meshes, value = inputs(session)
    expected, _ = routing.evaluate(session.engine, value)
    with ThreadPoolExecutor(2) as pool:
        results = list(pool.map(lambda _: routing.evaluate(session.engine, value)[0], range(4)))
    for result in results:
        np.testing.assert_allclose(result.array(), expected.array(), atol=1e-12, rtol=0)
    token = NativeCancellation(session.engine)
    token.set()
    import pytest

    with pytest.raises(ValueError, match="[Cc]ancel"):
        routing.evaluate(session.engine, value, token.handle)


def test_oversize_capture_not_retained(session):
    meshes, value = inputs(session)
    session.engine.routing_scenes.budget = 1
    scene = routing_scene.capture(session.engine, routing.arrays(value), 0.002, 0)
    assert scene.bytes > 1 and not session.engine.routing_scenes.retained()
    assert session.engine.routing_scenes.bytes == 0
