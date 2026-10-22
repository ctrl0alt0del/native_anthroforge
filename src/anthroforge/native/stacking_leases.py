"""A checked-out stacking session has exactly one multi-call owner, including groups."""

from collections.abc import Iterator
from contextlib import contextmanager

from .mesh import GeometryEngine
from .stacking import StackSession


@contextmanager
def acquire(engine: GeometryEngine, target: str) -> Iterator[StackSession]:
    cache = engine.stack_sessions
    value, epoch = cache.take((target,))
    native = value if value is not None else StackSession(engine)
    if value is not None and engine.resource_observer is not None:
        engine.resource_observer(native)
    yield native
    cache.restore((target,), native, native.bytes, epoch)
