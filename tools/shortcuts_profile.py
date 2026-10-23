"""Reproducible 0.3 headless timing and profiler attribution; excludes desktop latency."""

import json
import platform
import subprocess
import sys
from functools import partial
from pathlib import Path
from statistics import median
from time import perf_counter_ns
from zipfile import ZipFile

import numpy as np
from shortcuts_profile_workload import workload

from anthroforge.application.session import Session
from anthroforge.core.expressions import Symbol
from anthroforge.native import expressions
from anthroforge.native.mesh import INT64, pointer

OUTPUT = Path("build/shortcuts-profile")
SYMBOLS = (Symbol("t"), Symbol("r", dimension="LENGTH"))
SOURCE = "r*(sin(t)+cos(t))"


def timed(action, repeats=25, prepare=None):
    samples = []
    for _ in range(repeats):
        if prepare:
            prepare()
        start = perf_counter_ns()
        result = action()
        samples.append((perf_counter_ns() - start) / 1e6)
    return dict(
        median_ms=median(samples), min_ms=min(samples), max_ms=max(samples), samples_ms=samples
    ), result


def compile_cost(engine):
    compile_program = partial(expressions.compile, engine, SOURCE, SYMBOLS)
    cold, program = timed(compile_program, prepare=engine.expressions.clear)
    warm, reused = timed(compile_program)
    assert reused is program
    return dict(cold=cold, cached=warm, program_bytes=program.bytes), program


def native_inputs(program, values):
    integers, reals = expressions.frames(SYMBOLS, values)
    output_integer = np.empty(len(values), dtype=np.int64)
    output_real = np.empty(len(values))
    args = (
        program.handle,
        integers.ctypes.data_as(INT64),
        pointer(reals),
        len(values),
        output_integer.ctypes.data_as(INT64),
        pointer(output_real),
        0,
    )
    return args, output_real, (integers, reals, output_integer)


def batch_cost(program, count):
    values = [dict(t=index / count, r=0.03) for index in range(count)]
    packing, _ = timed(lambda: expressions.frames(SYMBOLS, values))
    args, output, owners = native_inputs(program, values)
    native, status = timed(lambda: program.engine.library.af_expression_evaluate(*args))
    program.engine.check(status)
    total, complete = timed(lambda: program.batch(values))
    t = np.arange(count) / count
    np.testing.assert_allclose(output, 0.03 * (np.sin(t) + np.cos(t)), atol=1e-14)
    np.testing.assert_array_equal(output, complete)
    assert owners  # Keep all borrowed C ABI buffers alive through every call.
    return dict(frames=count, packing=packing, native=native, adapter_total=total)


def microbench():
    session = Session()
    try:
        compilation, program = compile_cost(session.engine)
        batches = [batch_cost(program, count) for count in (1, 256, 4096)]
        return dict(compilation=compilation, batches=batches)
    finally:
        session.close()


def application_workload(recording):
    session = Session()
    try:
        if recording:
            session.command("profile.start", seconds=120)
        result = workload(session)
        if recording:
            path = OUTPUT / "driver-paths.afprofile.zip"
            session.command("profile.stop", path=str(path), wait=True)
            result["profile"] = profile_evidence(path)
        return result
    finally:
        session.close()


def profile_evidence(path):
    with ZipFile(path) as archive:
        summary = json.loads(archive.read("summary.json"))
        manifest = json.loads(archive.read("manifest.json"))
    return dict(
        path=str(path),
        durations=stages(summary),
        diagnostics=summary["diagnostics"],
        losses=manifest["losses"],
        limitations=manifest["limitations"],
    )


def stages(summary):
    durations = {
        key: value
        for key, value in summary["durations"].items()
        if key.startswith(("task/", "native/af_expression", "native/af_parametric"))
    }
    assert "native/af_parametric_path" in durations
    assert "native/af_expression_evaluate" in durations
    return durations


def measurements():
    return dict(
        revision=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        platform=platform.platform(),
        python=platform.python_version(),
        microbench=microbench(),
        unrecorded=application_workload(False),
        recorded=application_workload(True),
    )


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    report = measurements()
    assert not any(name.startswith(("PySide6", "PyQt")) for name in sys.modules)
    report["scope"] = (
        "Headless synthetic workload; no GUI/GPU latency or before/after speedup claim."
    )
    (OUTPUT / "measurements.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Headless 0.3 profile written to {OUTPUT}; numerical outputs verified.")


if __name__ == "__main__":
    main()
