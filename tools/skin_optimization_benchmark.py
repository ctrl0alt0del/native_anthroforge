"""Isolated, fixed-input draft-skin timing, OS peak memory and exact-output evidence."""

import argparse
import hashlib
import json
import os
import platform
import sys
from contextlib import contextmanager
from pathlib import Path
from time import perf_counter

import numpy as np
import psutil


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--library", type=Path)
    parser.add_argument("--addon", type=Path)
    parser.add_argument("--resolution", type=int, default=160)
    parser.add_argument("--budget", type=int, default=364835430)
    parser.add_argument("--save-arrays", action="store_true")
    parser.add_argument("--profile", type=Path)
    args = parser.parse_args()
    validate_arguments(parser, args)
    return args


def validate_arguments(parser, args):
    if bool(args.library) == bool(args.addon):
        parser.error("Choose exactly one of --library or --addon.")
    if args.profile and args.addon:
        parser.error("The application profiler is available only with --library.")


def memory():
    process = psutil.Process()
    info, cpu = process.memory_info(), process.cpu_times()
    return dict(
        rss=info.rss,
        peak_rss=getattr(info, "peak_wset", None),
        peak_commit=getattr(info, "peak_pagefile", None),
        cpu_seconds=cpu.user + cpu.system,
        available=psutil.virtual_memory().available,
    )


def measure(report, label, function, *args, **kwargs):
    started = perf_counter()
    result = function(*args, **kwargs)
    report[label] = dict(seconds=perf_counter() - started, **memory())
    print(json.dumps({label: report[label]}), flush=True)
    return result


def fingerprint(array):
    value = np.ascontiguousarray(array)
    return dict(
        shape=list(value.shape), dtype=str(value.dtype), sha256=hashlib.sha256(value).hexdigest()
    )


def arrays_result(vertices, triangles, binding):
    return dict(
        vertices=np.asarray(vertices, dtype=np.float64),
        faces=np.asarray(triangles, dtype=np.int64),
        **binding,
    )


def native_prepare(engine, data, args):
    from anthroforge.core.skin import EnvelopeSettings
    from anthroforge.native.skin_fields import prepare

    return prepare(
        engine,
        data["vertices"],
        data["triangles"],
        data["skeletal"],
        data.get("collagen", np.ones(len(data["vertices"]))),
        settings=EnvelopeSettings(*data.get("settings", ())),
        resolution=args.resolution,
        budget=args.budget,
    )


def native(args, data, report):
    os.environ["ANTHROFORGE_NATIVE_LIBRARY"] = str(args.library.resolve())
    with native_engine(args) as engine:
        fields = measure(report, "fields", native_prepare, engine, data, args)
        scene = measure(report, "scene", native_scene, engine, data)
        try:
            return native_output(args, report, scene, fields)
        finally:
            scene.close()
            fields.close()


@contextmanager
def native_engine(args):
    from anthroforge.application.session import Session
    from anthroforge.native.mesh import GeometryEngine

    if not args.profile:
        yield GeometryEngine()
        return
    session = Session("Skin qualification")
    try:
        session.command("profile.start", seconds=600)
        yield session.engine
    finally:
        session.command("profile.stop", path=str(args.profile.resolve()), wait=True)
        session.close()


def native_scene(engine, data):
    from anthroforge.native.skin_gaps import create

    return create(engine, *(data[k] for k in ("vertices", "triangles", "owners", "policies")))


def native_output(args, report, scene, fields):
    result = measure(report, "envelope", scene.envelope, fields, budget=args.budget)
    binding = measure(report, "bindings", scene.bind, result.mesh)
    report["generation_peak"] = memory()
    report.update(
        resolution=fields.resolution, voxel=fields.voxel, diagnostics=result.diagnostics.report()
    )
    report["fields_hashes"] = [fingerprint(fields.array(i)) for i in range(4)]
    arrays = arrays_result(result.mesh.array(0).copy(), result.mesh.array(3).copy(), binding)
    return arrays


def source_part(data, owner, length):
    from core.draft_skin.model import SkinSource

    triangles = data["triangles"][data["owners"] == owner]
    lo, hi = int(triangles.min()), int(triangles.max()) + 1
    policy = data["policies"][owner]
    kind = "SCP" if policy[2] else "VCP"
    identity = owner, kind, str(owner), "ORIGINAL", str(owner)
    collagen = data.get("collagen", np.ones(len(data["vertices"])))
    geometry = data["vertices"][lo:hi], triangles - lo, collagen[lo:hi]
    source = SkinSource(*identity, *geometry, float(policy[0] / length), float(policy[1]))
    return source, (lo, hi)


def source_capture(args, data):
    from core.draft_skin.model import SkinCapture, SkinSolverSettings

    length = float(np.ptp(data["vertices"], axis=0).max())
    parts = [source_part(data, i, length) for i in range(len(data["policies"]))]
    verify_spans(parts, data)
    xyz, settings = data["vertices"], SkinSolverSettings(*data.get("settings", ()))
    inputs = "benchmark", tuple(s for s, _ in parts), xyz.min(0), xyz.max(0), "fixed", 0
    capture = SkinCapture(*inputs, args.resolution, settings=settings)
    verify_capture(capture, data)
    return capture


def verify_spans(parts, data):
    spans = [span for _, span in parts]
    expected = [(0 if i == 0 else spans[i - 1][1], hi) for i, (_, hi) in enumerate(spans)]
    if spans != expected or spans[-1][1] != len(data["vertices"]):
        raise ValueError("Capture must retain complete contiguous source vertex blocks.")


def verify_capture(capture, data):
    from core.draft_skin.gap_native import _arrays

    names = "vertices", "triangles", "owners", "policies"
    for name, actual in zip(names, _arrays(capture), strict=True):
        np.testing.assert_array_equal(actual, data[name], err_msg=f"Addon input changed: {name}")


def source_binding(binding):
    names = dict(
        owners="source_indices",
        triangles="triangle_indices",
        barycentric="barycentric",
        weights="weights",
        offsets="normal_offsets",
        support="support",
    )
    return {name: getattr(binding, attr) for name, attr in names.items()}


def addon(args, data, report):
    sys.path.insert(0, str(args.addon.resolve()))
    from core.draft_skin import gap_solver, solver

    # Fix the same existing budget input in both adapters; no numerical code is patched.
    gap_solver.worker_memory_limit = solver.worker_memory_limit = lambda: args.budget
    capture = source_capture(args, data)
    prepared = measure(report, "fields", solver._prepare_capture, capture, None, None)
    return addon_output(capture, report, prepared)


def addon_output(capture, report, prepared):
    from core.draft_skin.gap_solver import reconstruct

    resolution, grid, distances, fields = prepared
    inputs = capture, fields, grid[0], grid[2], distances, None, None
    result, binding, diagnostics = measure(report, "envelope_and_bindings", reconstruct, *inputs)
    report["generation_peak"] = memory()
    report.update(resolution=resolution, voxel=grid[2], diagnostics=diagnostics)
    report["fields_hashes"] = [
        fingerprint(v) for v in (*fields, fields[0] + fields[2] * (fields[1] - fields[0]))
    ]
    return arrays_result(result[0], result[1], source_binding(binding))


def environment():
    return dict(
        platform=platform.platform(),
        logical_cpus=psutil.cpu_count(),
        physical_cpus=psutil.cpu_count(logical=False),
        total_ram=psutil.virtual_memory().total,
        start=memory(),
        system_cpu_percent=psutil.cpu_percent(interval=0.2),
    )


def metadata(args, data):
    native_hash = hashlib.sha256(args.library.read_bytes()).hexdigest() if args.library else None
    return dict(
        **environment(),
        capture=str(args.capture.resolve()),
        input_hashes={k: fingerprint(v) for k, v in data.items()},
        library=str(args.library) if args.library else None,
        library_sha256=native_hash,
        requested_resolution=args.resolution,
        budget=args.budget,
        profiler=bool(args.profile),
    )


def save_report(args, report, output):
    stages = ("fields", "scene", "envelope", "bindings", "envelope_and_bindings")
    report["generation_seconds"] = sum(report[k]["seconds"] for k in stages if k in report)
    report["output_hashes"] = {k: fingerprint(v) for k, v in output.items()}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    if args.save_arrays:
        np.savez(args.output.with_suffix(".npz"), **output)
    print(
        json.dumps({"report": str(args.output), "seconds": report["generation_seconds"]}),
        flush=True,
    )


def main():
    args = arguments()
    with np.load(args.capture, allow_pickle=False) as saved:
        data = {k: saved[k] for k in saved.files}
    if len(data.get("segments", ())):
        raise ValueError("This benchmark requires SCP/VCP surface contributors only.")
    report = metadata(args, data)
    output = (native if args.library else addon)(args, data, report)
    save_report(args, report, output)


if __name__ == "__main__":
    main()
