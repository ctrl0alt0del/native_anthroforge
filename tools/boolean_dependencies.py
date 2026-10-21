"""Distribute exact-arithmetic headers and upstream notices used by the native build."""

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def dependencies():
    manifest = ROOT / "build/dev/boolean-dependencies.json"
    if not manifest.is_file():
        raise RuntimeError("Build native first to identify the Boolean dependency sources.")
    return {name: Path(path) for name, path in json.loads(manifest.read_text()).items()}


def notices(root):
    for path in root.iterdir():
        if path.is_file() and path.name.upper().startswith(("LICENSE", "COPYRIGHT")):
            yield path
        elif path.is_dir() and path.name.upper() == "LICENSES":
            yield from (p for p in path.rglob("*") if p.is_file())


def copy_notices(destination):
    for name, root in dependencies().items():
        for source in notices(root):
            target = destination / name / source.relative_to(root)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)


def archive_headers(archive):
    for name, root in dependencies().items():
        directory = root / ("include" if name == "cgal" else "boost")
        paths = (p for p in directory.rglob("*") if p.is_file())
        for source in (*notices(root), *paths):
            target = f"anthroforge/native/boolean/dependencies/{name}/"
            archive.write(source, target + source.relative_to(root).as_posix())
