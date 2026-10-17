"""Version-pinned native Qt collector; no Python callbacks on the render thread."""

import ctypes as c
import json
from time import perf_counter_ns

from PySide6.QtCore import QObject
from PySide6.QtGui import QGuiApplication
from shiboken6 import getCppPointer, wrapInstance

from .runtime import build_directory

INPUT_TYPES = {
    2: "mouse_press",
    3: "mouse_release",
    5: "mouse_move",
    6: "key_press",
    7: "key_release",
    31: "wheel",
}


def profiler_application():
    library = c.CDLL(str(build_directory() / "bin" / "af_profiler.dll"))
    library.af_profile_application.restype = c.c_void_p
    app = wrapInstance(library.af_profile_application(), QGuiApplication)
    app._profiler_library = library
    return app


class QtProfiler:
    def __init__(self):
        self.library = c.CDLL(str(build_directory() / "bin" / "af_profiler.dll"))
        self.library.af_profile_read.argtypes = [c.c_void_p, c.c_int, c.c_int]
        self.library.af_profile_window.argtypes = [c.c_void_p]
        self.library.af_profile_root.argtypes = [c.c_void_p]
        self.library.af_profile_clock.restype = c.c_int64
        before = perf_counter_ns()
        native = self.library.af_profile_clock()
        after = perf_counter_ns()
        self.clock_offset = (before + after) // 2 - native
        self.clock_error = (after - before) // 2
        self.library.af_profile_initialize()
        self.window, self.presentation = None, {}

    def attach(self, window, controller=None):
        self.window = window
        self.library.af_profile_window(getCppPointer(window)[0])
        if controller:
            self.library.af_profile_root(getCppPointer(controller)[0])

    def start(self):
        if self.window:
            self.presentation = presentation(self.window)
        self.library.af_profile_start()
        state = self.status()
        if state["failure"]:
            raise RuntimeError(state["failure"])

    def stop(self):
        self.library.af_profile_stop()

    def read(self, status=False):
        buffer = c.create_string_buffer(300_000)
        count = self.library.af_profile_read(buffer, len(buffer), int(status))
        if count < 0:
            raise RuntimeError("Qt profiler transfer exceeded its chunk budget")
        return buffer.value

    def drain(self):
        events = [json.loads(line) for line in self.read().splitlines()]
        for event in events:
            event["ts"] += self.clock_offset / 1000
        return events

    def status(self):
        return dict(
            json.loads(self.read(True)),
            bridge_clock_error_ns=self.clock_error,
            presentation=self.presentation,
        )

    def close(self):
        self.library.af_profile_shutdown()


def presentation(window):
    keyboard = window.findChild(QObject, "keyboardManager")
    bindings = keyboard.property("modifierBindings") if keyboard else {}
    return dict(
        width=window.width(),
        height=window.height(),
        pixel_ratio=window.devicePixelRatio(),
        modifier_bindings=bindings.toVariant() if hasattr(bindings, "toVariant") else bindings,
        input_types=INPUT_TYPES,
    )
