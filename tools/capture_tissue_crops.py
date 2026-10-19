"""Capture actual donor material clipping and clip-before-envelope composition."""

import hashlib
import importlib
import json
import sys
from pathlib import Path

import numpy as np


def planes(points):
    center = np.asarray(points).mean(axis=0).tolist()
    return [
        dict(origin=center, normal=[1, 0.35, 0], positive=True),
        dict(origin=center, normal=[1, 0.35, 0], positive=False),
        dict(origin=[100, 0, 0], normal=[1, 0, 0], positive=True),
    ]


def clip(module, row, plane, values):
    normal, origin = np.asarray(plane["normal"]), np.asarray(plane["origin"])
    settings = dict(normal=normal, offset=float(normal @ origin), keep_positive=plane["positive"])
    return module.clip_domain(row["points"], values, row["faces"], settings, row["labels"])


def single(module, row, index, plane):
    result = clip(module, row, plane, row["output"])
    return dict(
        source=index,
        plane=plane,
        vertices=result.inflated_vertices.tolist(),
        base=result.base_vertices.tolist(),
        faces=result.faces.tolist(),
        parts=result.face_parts.tolist(),
        origins=result.source_faces.tolist(),
    )


def envelope(module, compose, row, sources, index, plane):
    source = sources[row["source"] + 9]
    first, second = (clip(module, source, plane, row[k]) for k in ("first", "second"))
    vertices, faces, _, _ = compose.compose(
        first.inflated_vertices, second.inflated_vertices, first.faces
    )
    return dict(envelope=index, plane=plane, vertices=vertices.tolist(), faces=faces.tolist())


def captures(module, compose, sources, envelopes):
    rows = [
        single(module, sources[i], i, plane)
        for i in (0, 6, 9, 10)
        for plane in planes(sources[i]["points"])
    ]
    rows += [
        envelope(module, compose, envelopes[i], sources, i, plane)
        for i in (0, 1, 4, 5)
        for plane in planes(sources[envelopes[i]["source"] + 9]["points"])[:2]
    ]
    return rows


def main(addon, fixtures):
    sys.path.insert(0, str(addon))
    module = importlib.import_module("core.vcp.muscle_domain_clip")
    compose = importlib.import_module("core.vcp.muscle_envelope_native")
    sources = json.loads((fixtures / "smoothing.json").read_text())["cases"]
    envelopes = json.loads((fixtures / "envelopes.json").read_text())["cases"]
    source = addon / "core/vcp/muscle_domain_clip.py"
    data = dict(
        source=str(source.relative_to(addon)),
        sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        cases=captures(module, compose, sources, envelopes),
    )
    (fixtures / "crops.json").write_text(json.dumps(data, allow_nan=False) + "\n")


if __name__ == "__main__":
    main(*(Path(value) for value in sys.argv[sys.argv.index("--") + 1 :]))
