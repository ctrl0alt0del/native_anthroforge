"""Compare uncached confirmed queries with a pinned source/native baseline, without Qt."""

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def options():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--source", type=Path, default=ROOT / "src")
    parser.add_argument("--native", type=Path, default=ROOT / "build/dev/bin/af_native.dll")
    parser.add_argument("--actual", type=Path)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--reverse", action="store_true")
    return parser.parse_args()


def cases(engine, actual):
    from anthroforge.native import tissue_parts
    from tests.test_surface_query_modes import compound
    from tests.test_surface_query_reuse import clean_mesh, open_tissue
    from tests.test_tissue_intersection_policy import fixture

    names = ("cube", "radial", "disjoint", "open")
    result = {name: (clean_mesh(engine, name), None) for name in names}
    base, top = open_tissue(engine)
    result.update(temporary_closure=(top, base), cavity=(compound(engine), None))
    base, parts = fixture(engine)
    result["crossed_fixture"] = tissue_parts.evaluate(base, parts, "a", True), base
    if actual:
        result.update(actual_cases(engine, actual))
    return result


def actual_cases(engine, path):
    from dataclasses import replace

    from anthroforge.application.storage import read_package
    from anthroforge.core.tissues import TissueVCP
    from anthroforge.native import tissue_parts, tissue_smoothing

    document, resources = read_package(path, engine)
    item = next(obj for obj in document.objects if isinstance(obj, TissueVCP))
    base = resources.meshes[item.base_result.asset].mesh
    side = replace(item.parts[0].a, inflation=replace(item.parts[0].a.inflation, amount=0.599))
    parts = (replace(item.parts[0], a=side), *item.parts[1:])
    raw = tissue_parts.evaluate(base, parts, "a", item.reverse)
    smoothed, _ = tissue_smoothing.evaluate(base, raw, parts, "a")
    return dict(actual_base=(base, None), actual_crossed=(smoothed, base))


def signature(mesh):
    # Validation outside timing: ignore vertex/face ordering, retain triangle orientation.
    triangles = mesh.array(0)[mesh.array(3)]
    records = [min(tuple(np.roll(face, k, axis=0).ravel()) for k in range(3)) for face in triangles]
    values = np.asarray(sorted(records), dtype=np.float64)
    return hashlib.sha256(values.tobytes()).hexdigest()


def query(engine, source, base):
    from anthroforge.native import surface_queries

    engine.clear_caches()
    wall, cpu = time.perf_counter(), time.process_time()
    result = surface_queries.prepare(source, base, surface_queries.Mode.CONFIRMED)
    return result, dict(
        wall_ms=1000 * (time.perf_counter() - wall), cpu_ms=1000 * (time.process_time() - cpu)
    )


def measure(engine, pair, repeats):
    source, base = pair
    query(engine, source, base)
    trials = []
    for _ in range(repeats):
        result, timing = query(engine, source, base)
        trials.append(timing)
    return dict(
        triangles=source.counts[3],
        output_triangles=result.mesh.counts[3],
        trials=trials,
        shared=result.mesh.array(0).ctypes.data == source.array(0).ctypes.data,
        bytes=result.bytes,
        geometry=signature(result.mesh),
    )


def run(args):
    from anthroforge.native.mesh import GeometryEngine

    engine = GeometryEngine(args.native)
    inputs = list(cases(engine, args.actual).items())
    if args.reverse:
        inputs.reverse()
    records = {name: measure(engine, pair, args.repeats) for name, pair in inputs}
    return dict(
        native_sha256=hashlib.sha256(args.native.read_bytes()).hexdigest(),
        cases=records,
        source=str(args.source),
        baseline_load="uncontrolled desktop; serial trials",
        actual_sha256=hashlib.sha256(args.actual.read_bytes()).hexdigest() if args.actual else None,
    )


def main():
    args = options()
    sys.path[:0] = [str(args.source), str(ROOT)]
    report = run(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
