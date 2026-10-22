"""Shared Windows/Linux core qualification; does not claim desktop release acceptance."""

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from importlib.metadata import version
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "build/core/qualification"


def run(*arguments):
    print("+ " + " ".join(map(str, arguments)), flush=True)
    subprocess.run(arguments, cwd=ROOT, check=True)


def python(*arguments):
    run(sys.executable, *arguments)


def environment():
    name = {"win32": "af_native.dll", "darwin": "libaf_native.dylib"}.get(sys.platform)
    os.environ["ANTHROFORGE_NATIVE_LIBRARY"] = str(
        ROOT / "build/core/bin" / (name or "libaf_native.so")
    )
    os.environ.setdefault("CMAKE_BUILD_PARALLEL_LEVEL", "2")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "passed.json").unlink(missing_ok=True)


def static_checks():
    run("uv", "lock", "--check")
    python("-m", "ruff", "check", "src", "tests", "tools")
    python("-m", "ruff", "format", "--check", "src", "tests", "tools")
    python("-m", "mypy")


def native_checks(style):
    run("cmake", "--preset", "portable-core")
    run("cmake", "--build", "--preset", "portable-core")
    run("ctest", "--preset", "portable-core")
    if style:
        commands = json.loads((ROOT / "build/core/compile_commands.json").read_text())
        for path in sorted({entry["file"] for entry in commands}):
            # Upstream sources retain their own style; match check-native-style.ps1.
            if not Path(path).resolve().is_relative_to(ROOT / "native/vendor"):
                run("clang-tidy", path, "-p", "build/core", "--quiet")


def workflow_checks():
    python("-m", "pytest", "--junitxml", str(OUTPUT / "pytest.xml"))
    python("-m", "anthroforge", "doctor", "--require-native")
    python("tools/check_headless_workshop.py")
    run("uv", "build")
    python("tools/check_wheel.py")


def record_success(style):
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    report = dict(
        passed=True,
        revision=revision,
        platform=platform.platform(),
        python=platform.python_version(),
        packages={name: version(name) for name in ("numpy", "PySide6", "pytest", "cmake")},
        lock_sha256=hashlib.sha256((ROOT / "uv.lock").read_bytes()).hexdigest(),
        native_library=os.environ["ANTHROFORGE_NATIVE_LIBRARY"],
        native_style=style,
        scope="Portable core, pytest, headless workshop, wheel; excludes GUI release acceptance",
    )
    (OUTPUT / "passed.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native-style", action="store_true")
    args = parser.parse_args()
    environment()
    static_checks()
    native_checks(args.native_style)
    workflow_checks()
    record_success(args.native_style)


if __name__ == "__main__":
    main()
