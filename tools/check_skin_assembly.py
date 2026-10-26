"""Quantify complete assembly correspondence on shared source patches."""

import json
import sys
from pathlib import Path

import numpy as np

from anthroforge.native import skin_annuli, skin_loops, skin_stitch, topology
from anthroforge.native.mesh import GeometryEngine
from tools.check_skin_decimation import mesh


def quads(engine, points, faces):
    points, faces = np.array(points), np.array(faces)
    triangles = np.stack((faces[:, [0, 1, 2]], faces[:, [0, 2, 3]]), axis=1).reshape(-1, 3)
    return topology.restore(
        engine,
        [
            points,
            faces.ravel(),
            np.arange(len(faces) + 1) * 4,
            triangles,
            np.repeat(np.arange(len(faces)), 2),
        ],
    )


def inputs(engine, row):
    source = quads(engine, row["vertices"], row["faces"])
    proxy = mesh(engine, np.array(row["proxy_vertices"]), np.array(row["proxy_faces"]))
    loops = skin_loops.Loops(
        np.array(row["samples"]),
        [],
        np.array(row["pairs"]).reshape(-1, 2),
        [],
        np.array(row["symmetric"]),
    )
    annuli = skin_annuli.build(proxy, loops, row["plane"])
    return source, annuli


def polygons(faces):
    return np.array([min(tuple(np.roll(face, i)) for i in range(4)) for face in faces])


def compare(result, expected):
    mesh = result.topology.mesh
    return dict(
        error=float(np.max(np.abs(mesh.array(0) - expected["points"]))),
        connectivity=bool(
            np.array_equal(polygons(mesh.array(1).reshape(-1, 4)), polygons(expected["faces"]))
        ),
        regions=bool(np.array_equal(result.topology.regions, expected["regions"])),
        guides=bool(np.array_equal(result.topology.guides, expected["guides"])),
        transitions=result.transitions.tolist(),
        warning=result.warning,
    )


def check(engine, row):
    source, annuli = inputs(engine, row)
    try:
        result = skin_stitch.assemble(
            source, annuli, row["plane"], row.get("allow_unstitched", False)
        )
        return dict(name=row["name"], **compare(result, row["expected"]))
    except ValueError as error:
        if "error" not in row:
            raise
        return dict(name=row["name"], rejection=str(error), expected=row["error"])


def main():
    rows = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["cases"]
    engine = GeometryEngine()
    results = [check(engine, row) for row in rows]
    Path(sys.argv[2]).write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
