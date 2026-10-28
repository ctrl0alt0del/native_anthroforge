"""Whole-body preparation retention; disposable disk cache never changes user cache."""

import hashlib
import shutil
import sys
from contextlib import closing
from dataclasses import replace
from pathlib import Path
from time import perf_counter
from unittest.mock import patch

import psutil
from check_skin_weight_cache import load
from profile_cache_retention import cache_state, write
from profiler_system_load import system_load, system_times

from anthroforge.application.session import Session
from anthroforge.core.skin import DeformationSettings
from anthroforge.native import skin_deformation, skin_weight_cache


def isolated(output):
    source, target = skin_weight_cache.directory(), output / "weights"
    target.mkdir(parents=True, exist_ok=True)
    for path in source.glob("*.zip"):
        shutil.copy2(path, target / path.name)
    return target


def trial(session, arrays, settings, index, output):
    session.command("profile.start", seconds=360)
    clock = system_times()
    solver = skin_deformation.cached(session.engine, "whole-body-reference", arrays, settings)
    result = preparation_result(session, solver, settings, clock)
    if settings.constraint_strength == 100:
        result.update(identity_solve(solver, arrays))
    session.command("profile.stop", path=str(output / f"skin-{index}.afprofile.zip"), wait=True)
    write(output, f"skin-{index}", result)
    print(index, result["load"], result["retained"], flush=True)


def preparation_result(session, solver, settings, clock):
    return dict(
        load=system_load(clock),
        disk_status=solver.cache_status,
        retained=cache_state(session.engine.skin_preparations),
        memory=psutil.Process().memory_info()._asdict(),
        strength=settings.constraint_strength,
    )


def identity_solve(solver, arrays):
    start = perf_counter()
    points, diagnostics, predicted = solver.solve(arrays["samples"])
    digest = hashlib.sha256(
        points.tobytes() + diagnostics.tobytes() + predicted.tobytes()
    ).hexdigest()
    return dict(solve_seconds=perf_counter() - start, sha256=digest)


def run(output, project):
    output.mkdir(parents=True, exist_ok=True)
    arrays, cache = load(project)["arrays"], isolated(output)
    settings = DeformationSettings(method="FAST", fast_handles=128)
    with closing(Session()) as session, patch.object(skin_weight_cache, "directory", lambda: cache):
        for index, strength in enumerate((100, 110, 120, 100, 100)):
            trial(session, arrays, replace(settings, constraint_strength=strength), index, output)
    write(
        output,
        "disk",
        dict(
            files=len(list(cache.glob("*.zip"))),
            bytes=sum(p.stat().st_size for p in cache.glob("*.zip")),
        ),
    )


if __name__ == "__main__":
    run(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve())
