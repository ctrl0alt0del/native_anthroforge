"""Entry point for an isolated Python interpreter, including packaged application use."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from anthroforge.avbd_runtime import worker  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(worker.main())
