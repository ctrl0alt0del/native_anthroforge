"""Capture the original addon LE/FAST DLL on compact, reproducible owned inputs."""

import ctypes as c
import hashlib
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np

P = np.ctypeslib.ndpointer(dtype=np.float64, flags="C_CONTIGUOUS")
INT = np.ctypeslib.ndpointer(dtype=np.int32, flags="C_CONTIGUOUS")


CREATE_ARGS = [
    P,
    c.c_int,
    INT,
    c.c_int,
    P,
    c.c_int,
    P,
    c.c_int,
    P,
    c.c_int,
    c.c_int,
    c.c_double,
    c.c_char_p,
]


def library(root):
    lib = c.CDLL(str(root / "native/deformation/af_deformation_v1.dll"))
    lib.af_ad_error.restype = c.c_char_p
    lib.af_ad_create.argtypes = CREATE_ARGS
    lib.af_ad_create.restype = c.c_void_p
    lib.af_ad_destroy.argtypes = [c.c_void_p]
    lib.af_ad_destroy.restype = None
    lib.af_ad_solve.argtypes = [c.c_void_p, P, P, P, P]
    lib.af_ad_embedding.argtypes = [c.c_void_p, INT, P]
    lib.af_ad_areas.argtypes = [P, c.c_int, INT, c.c_int, c.c_int, P]
    return lib


CUBE = np.array(
    [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]],
    dtype=float,
)
CELLS = np.array(
    [[0, 1, 2, 6], [0, 2, 3, 6], [0, 3, 7, 6], [0, 7, 4, 6], [0, 4, 5, 6], [0, 5, 1, 6]],
    dtype=np.int32,
)


def arrays():
    cube, cells = CUBE, CELLS
    skin = np.vstack((cube * 0.9 + 0.05, [[0.5, 0.25, 0.7], [0.3, 0.8, 0.2], [1.05, 0.2, 0.4]]))
    return dict(
        proxy_vertices=cube * 1.7 + [0.1, -0.2, 0.8],
        proxy_tets=cells,
        vertices=skin * 1.7 + [0.1, -0.2, 0.8],
        samples=cube * 1.7 + [0.1, -0.2, 0.8],
        sample_weights=np.arange(1, 9, dtype=float) / 36,
    )


def targets(points):
    bent = points.copy()
    bent[2:4] += [0.12, -0.08, 0.17]
    bent[6:8] += [-0.07, 0.03, 0.2]
    return dict(
        identity=points,
        translation=points + [0.2, -0.1, 0.3],
        scale=points * [1.2, 0.8, 1.1],
        bent=bent,
    )


def normalization(data):
    points = data["vertices"]
    center = (points.max(0) + points.min(0)) * 0.5
    scale = np.ptp(points, axis=0).max()
    return center, scale


def prepare(lib, data, method, folder):
    center, scale = normalization(data)
    normalized = [
        np.ascontiguousarray((data[k] - center) / scale)
        for k in ("proxy_vertices", "vertices", "samples")
    ]
    proxy, points, samples = normalized
    tets = data["proxy_tets"]
    source = proxy, len(proxy), tets, len(tets), points, len(points), samples, len(samples)
    controls = data["sample_weights"], method, 5, 100.0, str(Path(folder) / "cancel").encode()
    handle = lib.af_ad_create(*source, *controls)
    if not handle:
        raise RuntimeError(lib.af_ad_error().decode())
    return handle, center, scale


def solve(lib, handle, target, data, center, scale):
    values = np.ascontiguousarray((target - center) / scale)
    output = np.empty_like(data["vertices"])
    predicted = np.empty_like(target)
    report = np.zeros(6)
    if not lib.af_ad_solve(handle, values, output, report, predicted):
        raise RuntimeError(lib.af_ad_error().decode())
    return dict(
        points=(output * scale + center).tolist(),
        predicted=(predicted * scale + center).tolist(),
        diagnostics=report.tolist(),
    )


def capture(lib, data, method):
    with TemporaryDirectory(prefix="af-source-skin-") as folder:
        handle, center, scale = prepare(lib, data, method, folder)
        try:
            rows = {
                name: solve(lib, handle, value, data, center, scale)
                for name, value in targets(data["samples"]).items()
            }
            return dict(cases=rows, **embedding(lib, handle, len(data["vertices"])))
        finally:
            lib.af_ad_destroy(handle)


def embedding(lib, handle, count):
    ids = np.empty((count, 4), np.int32)
    weights = np.empty(ids.shape)
    if not lib.af_ad_embedding(handle, ids, weights):
        raise RuntimeError(lib.af_ad_error().decode())
    return dict(embedding_indices=ids.tolist(), embedding_weights=weights.tolist())


def sampling(lib):
    points = arrays()["proxy_vertices"]
    faces = np.array(
        [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]],
        np.int32,
    )
    mass = np.zeros(len(points))
    lib.af_ad_areas(points, len(points), faces, len(faces), 4, mass)
    return dict(points=points.tolist(), faces=faces.tolist(), **sample_cdf(mass))


def sample_cdf(mass):
    keep = np.flatnonzero(mass > 0)
    cumulative = np.cumsum(mass[keep])
    count = min(80, len(keep))
    selected = np.unique(
        keep[np.searchsorted(cumulative, (np.arange(count) + 0.5) * cumulative[-1] / count)]
    )
    return dict(selected=selected.tolist(), mass=float(cumulative[-1]))


def source_hashes(root):
    files = (
        "native/deformation/af_deformation_v1.dll",
        "native/deformation/native.cpp",
        "native/deformation/model.hpp",
        "native/deformation/reduced.hpp",
        "native/deformation/elastic.hpp",
    )
    return {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in files}


def main(root, output):
    lib = library(root)
    data = arrays()
    hashes = source_hashes(root)
    result = dict(
        source=hashes,
        arrays={k: v.tolist() for k, v in data.items()},
        targets={k: v.tolist() for k, v in targets(data["samples"]).items()},
    )
    result["results"] = {
        name: capture(lib, data, method) for name, method in (("LE", 0), ("FAST", 2))
    }
    result["sampling"] = sampling(lib)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
