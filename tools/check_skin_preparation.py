"""Compare the same captured anatomical envelope through the app's native boundary."""

import hashlib
import json
import sys
from functools import partial
from pathlib import Path
from time import perf_counter

import numpy as np

from anthroforge.native import skin_density, skin_proxy, skin_symmetry
from anthroforge.native.mesh import GeometryEngine
from tools.check_skin_decimation import mesh


def measure(name, operation, expected, output, report):
    started = perf_counter()
    result = operation()
    seconds = perf_counter() - started
    points, faces = result.array(0).copy(), result.array(3).copy()
    target = expected[name + "_points"]
    error = float(np.max(np.abs(points - target))) if points.shape == target.shape else None
    equal = np.array_equal(faces, expected[name + "_faces"])
    report[name] = dict(seconds=seconds, max_error=error, connectivity_equal=equal)
    output.update({name + "_points": points, name + "_faces": faces})
    print(name, report[name], flush=True)
    return result


def compare(source, expected, destination):
    engine, output, report = GeometryEngine(), {}, {}
    original = mesh(engine, source["vertices"], source["triangles"])
    call = partial(measure, expected=expected, output=output, report=report)
    proxy = call("decimate", lambda: skin_proxy.decimate(original, 64000))
    smooth = call("smooth", lambda: skin_density.smooth_proxy(proxy))
    plane = np.r_[source["plane_origin"], source["plane_normal"]]
    call("half", lambda: skin_symmetry.half(smooth, plane))
    np.savez(destination, **output)
    return report


def main():
    source, expected, destination = map(Path, sys.argv[1:])
    with np.load(source, allow_pickle=False) as data, np.load(expected, allow_pickle=False) as ref:
        metadata = json.loads(str(ref["metadata"]))
        assert hashlib.sha256(source.read_bytes()).hexdigest() == metadata["sha256"]
        report = dict(source=metadata, native=compare(data, ref, destination))
    destination.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    assert all(
        row["max_error"] == 0 and row["connectivity_equal"] for row in report["native"].values()
    )


if __name__ == "__main__":
    main()
