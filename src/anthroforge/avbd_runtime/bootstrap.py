"""Entry point for an isolated Python interpreter, including packaged application use."""

import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

worker = importlib.import_module("avbd_runtime.worker")

if __name__ == "__main__":
    raise SystemExit(worker.main())
