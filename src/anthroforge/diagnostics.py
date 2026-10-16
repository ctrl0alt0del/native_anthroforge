"""Read-only environment inspection, without importing Qt or numerical packages."""

import platform
from importlib.metadata import PackageNotFoundError, version
from typing import Any

from anthroforge import __version__
from anthroforge.native.bridge import NativeEngine


def package_version(name: str) -> str | None:
    try:
        return version(name)
    except PackageNotFoundError:
        return None


def native_status() -> dict[str, Any]:
    try:
        engine = NativeEngine()
        return {"available": True, "abi": engine.abi_version, "path": str(engine.path)}
    except (OSError, RuntimeError) as error:
        return {"available": False, "error": str(error)}


def environment_report() -> dict[str, Any]:
    packages = ("PySide6", "numpy", "scipy", "scikit-image", "pyinstantmeshes", "pytetwild")
    return {
        "application": __version__,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "native": native_status(),
        "packages": {name: package_version(name) for name in packages},
    }
