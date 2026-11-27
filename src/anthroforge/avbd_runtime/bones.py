"""Resume only an accepted complete SCP prefix, including its warm material state."""

import shutil
from itertools import groupby
from pathlib import Path
from typing import Any

import numpy as np

from . import root_seed, worker

FILES = ("input.bin", "local-input/input.bin", "local-input/frame.bin")
SURFACE = ("latest.bin", "faces.bin")
WARM = (
    *SURFACE,
    "edge-metrics.bin",
    "checkpoint-velocity.bin",
    "checkpoint-contacts.bin",
    "acceptance.json",
)


def run(recipe: Any, output: Path, resume: Any, root_vertices: int = 402) -> Any:
    root = output / "bones"
    root.mkdir()
    run = worker.module("skin_bone_run").BoneRun(root, recipe)
    run.stages = root_seed.stages(root, run.meshes, recipe.frame, root_vertices)
    restore(run, resume.get("SCP"))
    complete(run, output)
    return run


def complete(run: Any, output: Path) -> None:
    remaining = run.steps[len(run.rows) :]
    for route, steps in groupby(remaining, key=lambda step: step.route):
        worker.module("skin_run_settings").options(True, hand=route == "region")
        with worker.module("local_skin_stage").shared_worker(
            run.root, len(run.rows), route
        ) as process:
            for step in steps:
                run.add(step, process)
                checkpoint(run, output)
    worker.module("skin_run_settings").options(True, hand=run.steps[-1].route == "region")
    worker.write(run.root / "stages.json", run.rows)


def restore(run: Any, record: Any) -> None:
    if record is None:
        return
    parent = run.root / ".resume"
    shutil.copytree(record["folder"], parent)
    state = record["state"]
    run.rows = [dict(row, folder=str(parent)) for row in state["rows"]]
    run.stages.parent = parent
    run.stages.obstacles = worker.module("capture_clavicle_l3").read_input(
        parent / "local-input/input.bin"
    )
    restore_groups(run)


def restore_groups(run: Any) -> None:
    for step, mesh in zip(run.steps[: len(run.rows)], run.meshes, strict=False):
        if step.route == "region":
            run.stages.regional = True
            run.stages.groups.setdefault(step.family, []).append(
                (mesh, tuple(np.asarray(v) for v in step.joint))
            )


def checkpoint(run: Any, output: Path) -> None:
    parent = run.stages.parent
    names = (*FILES, *("validated/" + n for n in SURFACE), *("solve/relaxation/" + n for n in WARM))
    files = {name: parent / name for name in names}
    rows = [{key: value for key, value in row.items() if key != "folder"} for row in run.rows]
    worker.receipt(output, "SCP", len(rows) - 1, files, dict(rows=rows))
