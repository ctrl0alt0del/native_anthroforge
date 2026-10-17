"""Run the authored primitive workshop through the real CLI and reopen its saved result."""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def invoke(directory, *arguments):
    process = subprocess.run(
        [sys.executable, "-m", "anthroforge", *arguments],
        cwd=directory,
        text=True,
        capture_output=True,
        timeout=120,
    )
    if process.returncode:
        raise RuntimeError(process.stdout + process.stderr)
    return process.stdout


def verify(state):
    assert state["entity_count"] == 4 and len(state["controls"]) == 2
    assert not state["save_blocked"]
    assert all(item["result"]["status"] == "ready" for item in state["entities"])
    primitives = [item for item in state["entities"] if item["primitive"]]
    assert {item["primitive"]["kind"] for item in primitives} == {"IMPORTED", "LOFT", "BODY"}
    assert all(item["result"]["asset"] for item in primitives)


def main():
    with tempfile.TemporaryDirectory(prefix="anthroforge-workshop-") as temporary:
        directory = Path(temporary)
        shutil.copytree(ROOT / "examples", directory / "examples")
        records = invoke(directory, "run", "examples/primitives.json").splitlines()
        assert records and all(json.loads(line)["ok"] for line in records)
        verify(json.loads(invoke(directory, "inspect", "primitives.anthroforge")))
    print(
        "Headless workshop: imported mesh, loft, body, Hook/lattice, thickness, save/reopen passed."
    )


if __name__ == "__main__":
    main()
