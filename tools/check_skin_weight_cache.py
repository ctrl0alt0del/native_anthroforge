"""Measure a fresh process's FAST preparation and fingerprint its numerical result."""

import argparse
import hashlib
import json
from pathlib import Path
from time import perf_counter
from zipfile import ZipFile

from anthroforge.core.skin import DeformationSettings
from anthroforge.native import skin_deformation
from anthroforge.native.mesh import GeometryEngine


def run(fixture, handles=5):
    engine = GeometryEngine()
    settings = DeformationSettings(method="FAST", fast_handles=handles)
    start = perf_counter()
    with skin_deformation.Preparation(engine, fixture["arrays"], settings) as solver:
        preparation = perf_counter() - start
        points, diagnostics, predicted = solver.solve(fixture["targets"]["identity"])
        digest = hashlib.sha256(
            points.tobytes() + diagnostics.tobytes() + predicted.tobytes()
        ).hexdigest()
        return dict(preparation_seconds=preparation, cache=solver.cache_status, sha256=digest)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--project", type=Path)
    parser.add_argument("--handles", type=int, default=5)
    options = parser.parse_args()
    fixture = load(options.project)
    report = run(fixture, options.handles)
    options.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report))


def load(project):
    from anthroforge.application.skin_storage import read_asset

    if project is None:
        return json.loads(Path("tests/fixtures/skin/deformation.json").read_text())
    with ZipFile(project) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        key = manifest["document"]["skin"]["reference"]
        data = read_asset(archive, key, manifest["skin_assets"][key])
    return dict(arrays=data.arrays, targets=dict(identity=data.arrays["samples"]))


if __name__ == "__main__":
    main()
