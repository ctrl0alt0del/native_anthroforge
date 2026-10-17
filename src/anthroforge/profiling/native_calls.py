"""Install call observation at registered C ABI boundaries only while recording."""

from functools import wraps
from typing import Any
from weakref import WeakSet


class NativeCalls:
    def __init__(self, profiler):
        self.profiler, self.engines = profiler, WeakSet()
        self.originals = {}

    def attach(self, engine: Any) -> None:
        if engine in self.engines:
            return
        self.engines.add(engine)
        engine.profile_bind = lambda name, function: self.bind(engine, name, function)
        if self.profiler.active:
            self.install_engine(engine)

    def install_engine(self, engine):
        for name, function in list(vars(engine.library).items()):
            if name.startswith("af_") and callable(function):
                self.bind(engine, name, function)

    def detach(self, engine: Any) -> None:
        for key, (library, name, function) in list(self.originals.items()):
            if library is engine.library:
                setattr(library, name, function)
                del self.originals[key]
        self.engines.discard(engine)
        engine.profile_bind = None

    def bind(self, engine, name, function):
        key = id(engine.library), name
        if not self.profiler.active or key in self.originals:
            return
        self.originals[key] = (engine.library, name, function)
        setattr(engine.library, name, self.wrap(name, function))

    def wrap(self, name, function):
        @wraps(function)
        def invoke(*args):
            return self.profiler.call("native", name, function, *args)

        invoke._profile_original = function
        return invoke

    def start(self):
        for engine in self.engines:
            self.install_engine(engine)

    def stop(self):
        for library, name, function in self.originals.values():
            setattr(library, name, function)
        self.originals.clear()
