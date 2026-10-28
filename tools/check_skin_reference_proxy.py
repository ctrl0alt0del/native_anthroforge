"""Compare the actual addon reference Decimate path with the standalone native subset."""

import argparse
import json
import sys
from pathlib import Path
from time import perf_counter

import numpy as np


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("blender", "native", "compare"))
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--addon", type=Path)
    values = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    return parser.parse_args(values)


def source(path):
    with np.load(path, allow_pickle=False) as data:
        names = ("input_points", "input_faces") if "input_points" in data else ("vertices", "faces")
        return tuple(data[name].copy() for name in names)


def blender(points, faces, addon):
    sys.path[:0] = [str(addon), str(addon.parent)]
    import bpy
    from workers.deformation_reference import decimate

    output = decimate(points, faces)
    return *output, dict(
        engine="addon", blender=bpy.app.version_string, threads=bpy.context.scene.render.threads
    )


def native(points, faces):
    from anthroforge.native import skin_proxy
    from anthroforge.native.mesh import GeometryEngine
    from tools.check_skin_decimation import mesh

    engine = GeometryEngine()
    original = mesh(engine, points, faces)
    result = skin_proxy.reference(original)
    return result.array(0).copy(), result.array(3).copy(), dict(engine="standalone")


def compare(folder, output):
    with np.load(folder / "blender.npz") as expected, np.load(folder / "native.npz") as actual:
        for key in ("points", "faces"):
            np.testing.assert_array_equal(actual[key], expected[key])
        details = {
            name: json.loads(str(data["metadata"]))
            for name, data in (("blender", expected), ("native", actual))
        }
        details.update(exact_positions=True, exact_triangles=True, faces=len(actual["faces"]))
    output.write_text(json.dumps(details, indent=2), encoding="utf-8")
    print(json.dumps(details, indent=2))


def main():
    args = arguments()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.mode == "compare":
        compare(args.source, args.output)
        return
    points, faces = source(args.source)
    start = perf_counter()
    result = blender(points, faces, args.addon) if args.mode == "blender" else native(points, faces)
    vertices, polygons, metadata = result
    metadata.update(seconds=perf_counter() - start, input_triangles=len(faces), target=64000)
    np.savez(args.output, points=vertices, faces=polygons, metadata=json.dumps(metadata))
    print(json.dumps(metadata))


if __name__ == "__main__":
    main()
