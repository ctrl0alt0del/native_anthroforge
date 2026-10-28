"""Qt geometry CPU-copy probe only; no GPU timing or application state mutation."""

from statistics import median
from time import perf_counter

from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlComponent
from shiboken6 import delete


def probe(renderer, controller):
    component = QQmlComponent(renderer.engine)
    component.setData(b"import AnthroForge.Native 1.0\nMeshGeometry {}", QUrl())
    geometry = component.create()
    assert geometry is not None, component.errors()
    try:
        return samples(geometry, tuple(controller.render_model.leases.values()))
    finally:
        delete(geometry)
        delete(component)


def samples(geometry, meshes):
    values = [copies(geometry, meshes) for _ in range(5)]
    return dict(
        samples=values,
        median_seconds=median(s["seconds"] for s in values),
        scope="CPU asset setter/first-chunk copy; detached geometry, no GPU upload",
    )


def copies(geometry, meshes):
    size = sum(min(16384, m.counts[3]) * 72 for m in meshes)
    start = perf_counter()
    for mesh in meshes:
        geometry.setProperty("assetId", mesh.handle)
    return dict(seconds=perf_counter() - start, bytes=size, count=len(meshes))
