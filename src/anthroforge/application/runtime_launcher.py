"""Locate this application for isolated numerical and rendering commands."""

import sys
from pathlib import Path


def launcher() -> list[str]:
    # Nuitka's sys.executable may name an interpreter; argv[0] names the portable app.
    if "__compiled__" in globals():
        return [str(Path(sys.argv[0]).resolve()), "--cli"]
    return [sys.executable, "-m", "anthroforge"]
