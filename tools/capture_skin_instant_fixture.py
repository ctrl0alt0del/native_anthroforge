"""Run the addon's pinned CPython-3.11 backend in background Blender on compact inputs."""

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np


def run(addon, output):
    sys.path.insert(0, str(addon))
    from adapters.topology.vendor import ensure_worker_dependencies
    from core.native_platform import python_executable

    vendor = ensure_worker_dependencies()
    inputs = json.loads((output.parent / "instant-inputs.json").read_text())
    worker = [python_executable(), addon / "workers/topology_instant_worker.py"]
    with TemporaryDirectory(prefix="af-instant-parity-") as folder:
        cases = [capture(row, Path(folder), vendor, worker) for row in inputs]
    source = addon / "adapters/topology/instant_api.py"
    data = dict(
        source=str(source), sha256=hashlib.sha256(source.read_bytes()).hexdigest(), cases=cases
    )
    output.write_text(json.dumps(data), encoding="utf-8")


def capture(row, folder, vendor, worker):
    source, output = folder / "input.npz", folder / "result.npz"
    np.savez(source, vertices=np.asarray(row["vertices"]), faces=np.asarray(row["triangles"]))
    command = arguments(worker, source, output, vendor, row["target"])
    subprocess.run(command, check=True, timeout=300, creationflags=subprocess.CREATE_NO_WINDOW)
    with np.load(output) as result:
        return row | dict(
            expected_vertices=result["vertices"].tolist(), expected_quads=result["faces"].tolist()
        )


def arguments(worker, source, output, vendor, count):
    values = (
        *worker,
        "--input",
        source,
        "--output",
        output,
        "--vendor",
        vendor,
        "--target-vertices",
        count,
    )
    return list(map(str, values))


if __name__ == "__main__":
    values = sys.argv[sys.argv.index("--") + 1 :]
    run(Path(values[0]), Path(values[1]))
