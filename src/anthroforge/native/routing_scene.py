"""Leased immutable collision captures, reusable across curves and solve attempts."""

import ctypes as c

from .mesh import D, GeometryEngine, U, pointer


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_routing_scene_capture", [c.POINTER(U), D, c.c_int, c.c_double, U], U)
    engine.bind("af_routing_scene_release", [U], None)
    engine.bind("af_routing_scene_bytes", [U], U)


class RoutingScene:
    def __init__(self, engine: GeometryEngine, handle: int) -> None:
        engine.check(not handle)
        self.engine, self.handle = engine, handle
        self.bytes = int(engine.library.af_routing_scene_bytes(handle))
        if engine.resource_observer is not None:
            engine.resource_observer(self)

    def __del__(self) -> None:
        if getattr(self, "handle", 0):
            self.engine.library.af_routing_scene_release(self.handle)


def capture(engine, packed, radius, cancel):
    _, _, handles, matrices, _ = packed
    key = handles.tobytes(), matrices.tobytes(), radius
    cached = engine.routing_scenes.get(key)
    if cached is not None:
        return cached
    handle = engine.library.af_routing_scene_capture(
        handles.ctypes.data_as(c.POINTER(U)), pointer(matrices), len(handles), radius, cancel
    )
    scene = RoutingScene(engine, handle)
    size = scene.bytes + len(key[0]) + len(key[1]) + 1024
    return engine.routing_scenes.store(key, scene, size)
