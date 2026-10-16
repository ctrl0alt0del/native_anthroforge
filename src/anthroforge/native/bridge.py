"""Native library discovery and the stable shared C ABI."""

import ctypes
import os
import sys
from collections.abc import Sequence
from pathlib import Path


def library_path() -> Path:
    override = os.environ.get("ANTHROFORGE_NATIVE_LIBRARY")
    if override:
        return Path(override).resolve()
    names = {"win32": "af_native.dll", "darwin": "libaf_native.dylib"}
    name = names.get(sys.platform, "libaf_native.so")
    bundled = Path(__file__).resolve().parents[1] / "_runtime" / "bin" / name
    if bundled.is_file():
        return bundled
    return Path(__file__).resolve().parents[3] / "build" / "dev" / "bin" / name


class NativeEngine:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or library_path()
        self.library = ctypes.CDLL(str(self.path))
        self._configure()
        if self.abi_version != 1:
            raise RuntimeError(f"Unsupported native ABI: {self.abi_version}")

    def _configure(self) -> None:
        pointer = ctypes.POINTER(ctypes.c_double)
        self.library.af_abi_version.argtypes = []
        self.library.af_abi_version.restype = ctypes.c_uint32
        self.library.af_bounds3d.argtypes = [pointer, ctypes.c_uint64, pointer]
        self.library.af_bounds3d.restype = ctypes.c_int

    @property
    def abi_version(self) -> int:
        return int(self.library.af_abi_version())

    def bounds(self, coordinates: Sequence[float]) -> tuple[float, ...]:
        if not coordinates or len(coordinates) % 3:
            raise ValueError("Expected one or more packed XYZ positions.")
        source = (ctypes.c_double * len(coordinates))(*coordinates)
        result = (ctypes.c_double * 6)()
        status = self.library.af_bounds3d(source, len(coordinates) // 3, result)
        if status != 0:
            raise ValueError("Native geometry validation failed; positions must be finite.")
        return tuple(result)
