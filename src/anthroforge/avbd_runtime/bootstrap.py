"""Entry point for an isolated Python interpreter, including packaged application use."""

import importlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def isolate_bundle() -> None:
    root = Path(sys.argv[1]).resolve()
    if not (root / "manifest.json").is_file():
        return
    os.environ.pop("ANTHROFORGE_NATIVE_LIBRARY", None)
    os.environ.pop("PYTHONPATH", None)
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    sys.dont_write_bytecode = True
    system = Path(os.environ["SystemRoot"])
    os.environ["PATH"] = os.pathsep.join(
        (str(root / "python"), str(system / "System32"), str(system))
    )


isolate_bundle()
worker = importlib.import_module("avbd_runtime.worker")

if __name__ == "__main__":
    raise SystemExit(worker.main())
