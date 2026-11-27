"""Stage the qualified AVBD worker as a private, relocatable application runtime."""

import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

from avbd_sources import archive, notices

TOOLS = Path(__file__).resolve().parent
NATIVE = Path("build/avbd-envelope/cuda-native")
GEOGRAM = Path("build/avbd-envelope/quality-mesh-tools/geogram-build/bin")
HAND = Path("build/avbd-envelope/hand-web-policy-20261120")
REQUIRED = (
    "python/python.exe",
    "python/python312._pth",
    "tools/runtime/skin/application_worker.py",
    str(NATIVE / "af_instant_solver_resident.exe"),
    str(NATIVE / "af_vcp_clearance_solver.exe"),
    str(GEOGRAM / "af_quality_geogram.exe"),
    "src/anthroforge/_runtime/bin/af_native.dll",
)


def source_root():
    value = os.environ.get("AF_AVBD_SOURCE") or os.environ.get("ANTHROFORGE_AVBD_RUNTIME")
    if not value:
        raise RuntimeError("Packaging requires AF_AVBD_SOURCE pointing to qualified AVBD inputs.")
    root = Path(value).resolve()
    if not (root / "tools/runtime/skin/application_worker.py").is_file():
        raise ValueError("The AVBD build input does not contain the qualified worker.")
    return root


def copy_file(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def copy_sources(root, target):
    for directory in ("src/anthroforge", "tools/runtime", "tools/geometry_viewer"):
        for path in (root / directory).rglob("*"):
            if path.is_file() and path.suffix in (".py", ".json", ".txt"):
                copy_file(path, target / path.relative_to(root))
    for name in ("tools/experiments/cuda_voxel_bones/run.py", "LICENSE"):
        copy_file(root / name, target / name)


def copy_native(root, target):
    for directory in (NATIVE, GEOGRAM, HAND, Path("build/avbd-envelope/runtime-support")):
        files = list((root / directory).glob("*.exe"))
        if not files:
            raise FileNotFoundError(root / directory)
        for path in files:
            copy_file(path, target / path.relative_to(root))
    shutil.copytree(
        root / HAND / "deps", target / HAND / "deps", ignore=shutil.ignore_patterns(".lock")
    )
    for name in ("af_native.dll", "libomp.dll"):
        copy_file(root / "build/dev/bin" / name, target / "src/anthroforge/_runtime/bin" / name)


def copy_crt(target):
    redist = Path(os.environ["VCToolsRedistDir"]) / "x64"
    directories = list(redist.glob("Microsoft.VC*.CRT"))
    if len(directories) != 1:
        raise RuntimeError(f"Expected one x64 VC runtime in {redist}.")
    for directory in (
        NATIVE,
        GEOGRAM,
        HAND,
        Path("build/avbd-envelope/runtime-support"),
        Path("python"),
    ):
        for path in directories[0].glob("*.dll"):
            copy_file(path, target / directory / path.name)


def file_records(target):
    records = {}
    for path in sorted(target.rglob("*")):
        if path.is_file() and path.suffix != ".pyc" and path != target / "manifest.json":
            with path.open("rb") as stream:
                digest = hashlib.file_digest(stream, "sha256").hexdigest()
            records[path.relative_to(target).as_posix()] = dict(
                size=path.stat().st_size, sha256=digest
            )
    return records


def write_manifest(root, target):
    for name in REQUIRED:
        if not (target / name).is_file():
            raise FileNotFoundError(target / name)
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    status = subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True)
    metadata = json.loads((target / "python.json").read_text())
    receipt = dict(schema=1, revision=revision, source_dirty=bool(status), **metadata)
    required = [p.relative_to(target).as_posix() for p in (target / "build").rglob("*.exe")]
    required += [p.relative_to(target).as_posix() for p in (target / "build").rglob("*.dll")]
    receipt.update(required=sorted(set(required + list(REQUIRED))), files=file_records(target))
    (target / "manifest.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")


def stage(target):
    root = source_root()
    if target.exists():
        raise FileExistsError(f"AVBD staging requires a fresh output directory: {target}")
    python = root / ".venv/Scripts/python.exe"
    subprocess.run(
        [str(python), "-I", str(TOOLS / "avbd_python_bundle.py"), str(target)], check=True
    )
    copy_sources(root, target)
    copy_native(root, target)
    copy_crt(target)
    archive(root, target)
    notices(target)
    write_manifest(root, target)
    return target
