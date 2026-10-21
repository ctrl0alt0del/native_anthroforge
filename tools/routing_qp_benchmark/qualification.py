"""Baseline instrumentation-cost comparison and separate runtime-profiler captures."""

import json
from dataclasses import replace

import numpy as np

from anthroforge.native.mesh import GeometryEngine
from anthroforge.profiling.service import RuntimeProfiler
from tools.profiler_system_load import system_load, system_times

from . import cases, harness
from .run import checked, save, warm_input

OUTPUT = cases.ROOT / "build/routing-piqp"
NAMES = ("addon-open-bent", "solver_fail1-24-fiber", "snapped_cube-64-fiber", "skull-AF_FIBER_1")


def prepare(engine, case):
    meshes, spec = cases.inputs(engine, case)
    path, result = checked(engine, spec, case)
    assert result["ok"], result
    return meshes, spec, path


def baseline_trial(engine, prepared, case, mode):
    meshes, spec, path = prepared
    value = warm_input(engine, spec, path, mode)
    result, timing = checked(engine, value, case)
    return timing


def overhead_case(engines, case):
    prepared = [prepare(engine, case) for engine in engines]
    np.testing.assert_array_equal(prepared[0][2].array(), prepared[1][2].array())
    rows, load = [], system_times()
    for index in range(30):
        for mode in ("cold", "warm"):
            for backend in (0, 1) if index % 2 else (1, 0):
                result = baseline_trial(engines[backend], prepared[backend], case, mode)
                rows.append(dict(result, backend=backend, mode=mode, round=index))
    return dict(name=case["name"], trials=rows, load=system_load(load), identical=True)


def profile_case(engine, case, profiler, backend):
    meshes, spec, path = prepare(engine, case)
    for mode in ("cold", "warm"):
        value = warm_input(engine, spec, path, mode)
        for _ in range(3):
            result, _ = profiler.call(
                "benchmark", case["name"] + "/" + mode, checked, engine, value, case
            )
            value = replace(value, warm=result) if mode == "warm" else value
    engine.clear_caches()


def profile(engine, selected, backend):
    profiler = RuntimeProfiler()
    profiler.native.attach(engine)
    harness.configure(engine, backend)
    profiler.start()
    try:
        for case in selected:
            profile_case(engine, case, profiler, backend)
    finally:
        profiler.stop(str(OUTPUT / f"{harness.BACKENDS[backend]}.afprofile.zip"), wait=True)
        profiler.native.detach(engine)


def main():
    engines = GeometryEngine(), harness.engine()
    harness.configure(engines[1], 0)
    selected = [case for case in cases.all_cases(True) if case["name"] in NAMES]
    result = [overhead_case(engines, case) for case in selected]
    save(OUTPUT / "overhead.json", result)
    for backend in range(3):
        profile(engines[1], selected, backend)
    print(json.dumps([row["name"] for row in result]))


if __name__ == "__main__":
    main()
