"""Copy an isolated CPython image and the worker's installed wheel dependency closure."""

import importlib.metadata as metadata
import json
import shutil
import sys
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

ROOTS = ("numpy", "scipy", "pyvista", "psutil", "pyinstantmeshes", "scikit-image")
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", "site-packages", "test", "tests")


def dependency_closure(names):
    pending, found = list(names), {}
    while pending:
        name = canonicalize_name(pending.pop())
        if name in found:
            continue
        distribution = metadata.distribution(name)
        found[name] = distribution
        for text in distribution.requires or ():
            requirement = Requirement(text)
            if requirement.marker is None or requirement.marker.evaluate({"extra": ""}):
                pending.append(requirement.name)
    return found


def copy_distribution(distribution, target):
    source_root = Path(distribution.locate_file("")).resolve()
    for relative in distribution.files or ():
        source = Path(distribution.locate_file(relative)).resolve()
        if not source.is_relative_to(source_root) or source.suffix == ".pyc":
            continue
        if not source.is_file():
            raise FileNotFoundError(source)
        destination = target / source.relative_to(source_root)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def copy_interpreter(target):
    base = Path(sys.base_prefix)
    target.mkdir(parents=True, exist_ok=True)
    for path in base.iterdir():
        if path.is_file() and (path.suffix.lower() in (".exe", ".dll") or "LICENSE" in path.name):
            shutil.copy2(path, target / path.name)
    for folder in ("Lib", "DLLs"):
        shutil.copytree(base / folder, target / folder, ignore=IGNORE)
    paths = "Lib\nDLLs\nLib/site-packages\n..\n../src\nimport site\n"
    (target / "python312._pth").write_text(paths, encoding="utf-8")


def main():
    if sys.platform != "win32" or sys.version_info[:2] != (3, 12):
        raise RuntimeError("The qualified AVBD image requires Windows CPython 3.12.")
    target = Path(sys.argv[1]).resolve()
    copy_interpreter(target / "python")
    distributions = dependency_closure(ROOTS)
    for distribution in distributions.values():
        copy_distribution(distribution, target / "python/Lib/site-packages")
    versions = {name: dist.version for name, dist in sorted(distributions.items())}
    details = dict(python=sys.version, distributions=versions)
    (target / "python.json").write_text(json.dumps(details, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
