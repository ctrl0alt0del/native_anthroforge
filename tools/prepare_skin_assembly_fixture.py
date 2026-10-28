"""Create owned shared inputs for native versus Blender assembly qualification."""

import json
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np

from anthroforge.native import skin_annuli
from anthroforge.native.mesh import GeometryEngine
from tools.check_skin_annuli import capture
from tools.check_skin_decimation import mesh

ROTATION = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])


def transform(row, paired):
    loops = capture(row)
    samples = loops.samples.copy()
    if paired:
        samples[:, :, :3] *= 0.6
        samples[:, :, 0] += 1.5
        other = samples.copy()
        other[:, :, (0, 3)] *= -1
        samples = np.concatenate((samples, other))
    samples[:, :, :3] = samples[:, :, :3] @ ROTATION.T
    samples[:, :, 3:] = samples[:, :, 3:] @ ROTATION.T
    pairs = np.array([[0, 1], [2, 3]]) if paired else loops.pairs
    return replace(loops, samples=samples, pairs=pairs, symmetric=np.ones(len(samples)))


def border(count, radius, center):
    t = np.arange(count) * 2 * np.pi / count
    inner = np.column_stack((radius * np.sin(t), np.zeros(count), radius * np.cos(t)))
    outer = inner * 2
    outer[:, 0] += 0.15
    vertices = np.vstack((inner, outer))
    vertices[:, 0] += center
    quads = [[i, (i + 1) % count, count + (i + 1) % count, count + i] for i in range(count)]
    return vertices, np.array(quads)


def source(paired, count=48):
    vertices, faces = border(count, 0.8 if paired else 1.3, 1.5 if paired else 0)
    if paired:
        other = vertices.copy()
        other[:, 0] *= -1
        faces = np.vstack((faces, faces[:, ::-1] + len(vertices)))
        vertices = np.vstack((vertices, other))
    return vertices, faces


def case(engine, row, name):
    paired = name == "paired"
    loops = transform(row, paired)
    plane = [0, 0, 0, 1, 0, 0] if name in ("centered", "paired") else None
    proxy = mesh(engine, np.array(row["vertices"]) @ ROTATION.T, np.array(row["faces"]))
    patches = skin_annuli.build(proxy, loops, plane).snapshot()
    vertices, faces = source(paired, 47 if "parity" in name else 48)
    result = dict(name=name, vertices=vertices.tolist(), faces=faces.tolist(), plane=plane)
    result.update(common_inputs(proxy, loops, patches))
    result["allow_unstitched"] = name == "parity-warning"
    return result


def common_inputs(proxy, loops, patches):
    return dict(
        proxy_vertices=proxy.array(0).tolist(),
        proxy_faces=proxy.array(1).reshape(-1, 3).tolist(),
        samples=loops.samples.tolist(),
        pairs=loops.pairs.tolist(),
        symmetric=loops.symmetric.tolist(),
        patch_samples=patches.samples.tolist(),
        patch_faces=patches.quads.tolist(),
        patches=patches.patches.tolist(),
    )


def oriented_case(row):
    result = dict(row, name="closed-disconnected", pairs=[], patches=[])
    points = np.array(
        [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]],
        dtype=float,
    )
    points[6] += [0.2, 0.1, 0.4]
    faces = np.array(
        [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [3, 2, 6, 7], [0, 3, 7, 4], [1, 2, 6, 5]]
    )
    result["vertices"] = np.vstack((points, points * 2 + [4, 2, -1])).tolist()
    result["faces"] = np.vstack((faces, faces[:, ::-1] + 8)).tolist()
    return result


def main():
    row = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["cases"][0]
    engine = GeometryEngine()
    cases = [
        case(engine, row, name)
        for name in ("side", "centered", "paired", "parity-error", "parity-warning")
    ]
    cases.append(oriented_case(cases[0]))
    Path(sys.argv[2]).write_text(json.dumps(cases, separators=(",", ":")), encoding="utf-8")


if __name__ == "__main__":
    main()
