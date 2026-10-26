"""Qualify restored Fiber surfaces against the unmodified addon's area sampler."""

import argparse
import hashlib
import json
import sys
from importlib import import_module
from pathlib import Path

import numpy as np

from anthroforge.application.session import Session
from anthroforge.core.entities import IDENTITY
from anthroforge.native import paths, skin_capture

ROOT = Path(__file__).resolve().parents[1]


def native_path(engine, row):
    samples = np.zeros((len(row["points"]), 11))
    samples[:, :3] = row["points"]
    samples[:, 5] = samples[:, 6] = samples[:, 9] = 1
    return paths.restore(engine, samples, np.linspace(0, 1, len(samples)), row.get("closed", False))


def compare(session, row, sampler, lib):
    path = native_path(session.engine, row)
    mesh = skin_capture.fiber_bevel(path, IDENTITY, row["radius"])
    reference = row["output"]
    expected = sampler(
        lib, np.array(reference["vertices"]), np.array(reference["triangles"], np.int32)
    )
    actual = sampler(lib, mesh.array(0), np.ascontiguousarray(mesh.array(3), np.int32))
    np.testing.assert_array_equal(actual[0], expected[0])
    np.testing.assert_allclose(actual[1], expected[1], rtol=1e-6, atol=0)
    error = float(np.max(np.abs(mesh.array(0) - reference["vertices"])))
    return comparison_report(row["name"], actual, expected, error)


def comparison_report(name, actual, expected, error):
    return dict(
        name=name,
        area=actual[1],
        reference_area=expected[1],
        samples=len(actual[0]),
        max_vertex_error=error,
    )


def run(options):
    sys.path.insert(0, str(options.addon))
    construction = import_module("core.deformation.construction")
    lib = import_module("core.deformation.native").library()
    fixture = json.loads((ROOT / "tests/fixtures/skin/fiber_bevel.json").read_text())
    session = Session("Fiber sampler qualification")
    try:
        rows = [compare(session, row, construction.sample_surface, lib) for row in fixture["cases"]]
    finally:
        session.close()
    write_report(options.output, Path(construction.__file__), rows)


def write_report(output, source, rows):
    payload = dict(
        source=str(source), sha256=hashlib.sha256(source.read_bytes()).hexdigest(), cases=rows
    )
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("addon", type=Path)
    parser.add_argument("output", type=Path)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
