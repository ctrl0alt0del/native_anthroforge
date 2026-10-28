"""Load the pinned array extension without the package's visualization integration."""

import importlib.metadata
import importlib.util
import os
from functools import cache
from importlib.machinery import EXTENSION_SUFFIXES
from pathlib import Path
from types import ModuleType
from typing import Any

DIRECTORIES: list[Any] = []


def location() -> Path:
    if "__compiled__" in globals():
        return Path(__file__).resolve().parents[1] / "_runtime/tetrahedral/pytetwild"
    distribution = importlib.metadata.distribution("pytetwild")
    if distribution.version != "0.4.2":
        raise ValueError("Skin proxy preparation requires the pinned PyTetWild 0.4.2.")
    return Path(str(distribution.locate_file("pytetwild")))


def extension(folder: Path) -> Path:
    paths = [folder / ("PyfTetWildWrapper" + suffix) for suffix in EXTENSION_SUFFIXES]
    found = [path for path in paths if path.is_file()]
    if len(found) != 1:
        raise ValueError("The pinned tetrahedral native extension is missing or ambiguous.")
    return found[0]


@cache
def load() -> ModuleType:
    folder = location()
    libraries = folder.parent / "pytetwild.libs"
    if os.name == "nt" and libraries.is_dir():
        DIRECTORIES.append(os.add_dll_directory(str(libraries)))
    spec = importlib.util.spec_from_file_location("PyfTetWildWrapper", extension(folder))
    if spec is None or spec.loader is None:
        raise ValueError("Cannot load the tetrahedral native extension.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
