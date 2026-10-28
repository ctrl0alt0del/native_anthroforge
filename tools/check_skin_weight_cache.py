"""Measure a fresh process's FAST preparation and fingerprint its numerical result."""

import hashlib
import json
import sys
from pathlib import Path
from time import perf_counter

from anthroforge.core.skin import DeformationSettings
from anthroforge.native import skin_deformation
from anthroforge.native.mesh import GeometryEngine


def run(fixture):
    engine = GeometryEngine()
    settings = DeformationSettings(method="FAST", fast_handles=5)
    start = perf_counter()
    with skin_deformation.Preparation(engine, fixture["arrays"], settings) as solver:
        preparation = perf_counter() - start
        points, diagnostics, predicted = solver.solve(fixture["targets"]["identity"])
        digest = hashlib.sha256(
            points.tobytes() + diagnostics.tobytes() + predicted.tobytes()
        ).hexdigest()
        return dict(preparation_seconds=preparation, cache=solver.cache_status, sha256=digest)


def main():
    fixture = json.loads(Path("tests/fixtures/skin/deformation.json").read_text())
    report = run(fixture)
    Path(sys.argv[1]).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
