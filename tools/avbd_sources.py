"""Keep exact AVBD source inputs and bundled dependency notices with the release."""

import json
import zipfile
from pathlib import Path

FOLDERS = (
    "native",
    "tools/runtime",
    "tools/geometry_viewer",
    "tools/experiments/avbd_envelope",
    "tools/experiments/cuda_voxel_bones",
    "src",
    "licenses",
    "build/avbd-envelope/collision-vendor",
    "build/avbd-envelope/cuda-native/include",
    "build/avbd-envelope/quality-mesh-tools/geogram_1.10.1",
    "build/dev/_deps/af_query_boost-src/boost",
    "build/dev/_deps/af_query_cgal-src/include",
    "build/dev/_deps/af_query_cgal-src/cmake",
)
SKIP = {".git", "__pycache__", ".pytest_cache", "node_modules"}
BINARY = {".pyc", ".obj", ".lib", ".pdb", ".exe", ".dll", ".png", ".jpg", ".zip"}
NOTICES = (
    "Wheel licenses accompany each .dist-info directory in python/Lib/site-packages.",
    "CPython license: python/LICENSE.txt. Native dependency licenses accompany the sources.",
    "Microsoft VC runtime DLLs are redistributed app-local from the Visual Studio redist.",
    "AVBD's existing NVIDIA GPU/driver requirements are unchanged.",
)


def sources(root):
    for name in ("LICENSE", "pyproject.toml", "uv.lock", "CMakeLists.txt"):
        if (root / name).is_file():
            yield root / name
    for dependency in ("af_query_boost-src", "af_query_cgal-src"):
        yield from (root / "build/dev/_deps" / dependency).glob("LICENSE*")
    for directory in FOLDERS:
        for path in (root / directory).rglob("*"):
            if path.is_file() and not SKIP.intersection(path.parts) and path.suffix not in BINARY:
                yield path


def archive(root, target):
    with zipfile.ZipFile(target / "avbd-sources.zip", "w", zipfile.ZIP_DEFLATED) as output:
        for path in sources(root):
            if path.is_file():
                output.write(path, "avbd/" + path.relative_to(root).as_posix())


def notices(target):
    packages = json.loads((target / "python.json").read_text())["distributions"]
    lines = [
        "# Bundled AVBD runtime",
        "",
        "Exact inputs: manifest.json; sources: avbd-sources.zip.",
        "",
    ]
    lines += [f"- {name} {version}" for name, version in packages.items()]
    lines += ["", *NOTICES]
    (target / "NOTICE.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def include_source(archive, runtime):
    for name in ("avbd-sources.zip", "manifest.json", "NOTICE.md"):
        path = Path(runtime) / name
        if not path.is_file():
            raise FileNotFoundError(f"Build the AVBD runtime before archiving sources: {path}")
        archive.write(path, "anthroforge/avbd-runtime/" + name)
