"""Measure the addon's two-sided material sampling on retained envelope fixtures."""

import json
import sys
from pathlib import Path

import numpy as np
from capture_skin_deformation import library, sample_cdf


def capture(lib, case, faces, label):
    points = np.ascontiguousarray(case["vertices"], float)
    faces = np.ascontiguousarray(faces, np.int32)
    mass = np.zeros(len(points))
    lib.af_ad_areas(points, len(points), faces, len(faces), faces.shape[1], mass)
    samples = sample_cdf(mass)
    count = sum(index >= len(case["first"]) for index in samples["selected"])
    return record(case, label, len(points), len(faces), count, samples)


def record(case, label, vertices, faces, count, samples):
    return dict(
        case=case["source"],
        mode=label,
        vertex_count=vertices,
        face_count=faces,
        sample_count=len(samples["selected"]),
        second_side_samples=count,
        area=samples["mass"],
    )


def main(addon, fixtures, output):
    lib = library(addon)
    envelopes = json.loads((fixtures / "envelopes.json").read_text())["cases"]
    sources = json.loads((fixtures / "branches.json").read_text())["cases"]
    rows = []
    for case in envelopes:
        if not case["disabled"]:
            rows.append(capture(lib, case, sources[case["source"]]["faces"], "addon_capture_faces"))
            rows.append(capture(lib, case, case["faces"], "envelope_faces"))
    output.write_text(json.dumps(rows, indent=2) + "\n")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
