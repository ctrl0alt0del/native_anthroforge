import ctypes
import os
from contextlib import contextmanager
from pathlib import Path

import PySide6


def build_directory() -> Path:
    bundled = Path(__file__).resolve().parents[1] / "_runtime"
    if bundled.is_dir():
        return bundled
    default = Path(__file__).resolve().parents[3] / "build" / "dev"
    return Path(os.environ.get("AF_NATIVE_BUILD", default)).resolve()


def native_directories() -> list:
    if os.name != "nt":
        return []
    paths = [build_directory() / "bin", Path(PySide6.__file__).parent]
    return [os.add_dll_directory(str(path)) for path in paths if path.is_dir()]


def load_viewport_dependencies() -> list:
    if os.name != "nt":
        return []
    names = ("af_native.dll", "af_viewport.dll")
    return [ctypes.CDLL(str(build_directory() / "bin" / name)) for name in names]


@contextmanager
def native_runtime():
    handles = native_directories()
    try:
        libraries = load_viewport_dependencies()
        yield libraries
    finally:
        for handle in handles:
            handle.close()
