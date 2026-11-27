"""Verify release contents and import isolation with no developer environment."""

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

MODULES = ("skin_tissue_run", "vcp_default_sequence", "local_skin_stage", "skin_bone_run")


def verify_files(root):
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    for name, expected in manifest["files"].items():
        path = (root / name).resolve()
        assert path.is_relative_to(root), name
        assert path.stat().st_size == expected["size"], name
        with path.open("rb") as stream:
            assert hashlib.file_digest(stream, "sha256").hexdigest() == expected["sha256"], name
    return len(manifest["files"])


def probe_environment():
    excluded = ("PYTHON", "QT_", "QML_", "ANTHROFORGE_", "AF_")
    environment = {k: v for k, v in os.environ.items() if not k.upper().startswith(excluded)}
    system = Path(environment["SystemRoot"])
    environment["PATH"] = os.pathsep.join((str(system / "System32"), str(system)))
    return environment


def probe_code():
    return (
        "import sys,json,importlib; "
        f"[importlib.import_module('tools.runtime.skin.'+m) for m in {MODULES!r}]; "
        "files=[m.__file__ for m in sys.modules.values() if getattr(m,'__file__',None)]; "
        "print(json.dumps(files))"
    )


def probe(root):
    result = subprocess.run(
        [str(root / "python/python.exe"), "-I", "-B", "-c", probe_code()],
        cwd=root,
        env=probe_environment(),
        capture_output=True,
        text=True,
        timeout=90,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    paths = json.loads(result.stdout)
    assert all(Path(p).resolve().is_relative_to(root) for p in paths), paths
    return len(paths)


def main():
    root = Path(sys.argv[1]).resolve()
    print(json.dumps(dict(files=verify_files(root), isolated_imports=probe(root))))


if __name__ == "__main__":
    main()
