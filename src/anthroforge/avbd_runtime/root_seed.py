"""Initial sampling policy over the qualified native seed and unchanged later stages."""

import shutil
from contextlib import closing
from pathlib import Path
from time import perf_counter
from typing import Any

import numpy as np

from . import worker


def stages(root: Path, meshes: Any, frame: Path, vertices: int) -> Any:
    base = worker.module("local_skin_stage").SkinStages

    # The numerical runtime is loaded only inside its isolated worker process.
    class InitialRootStages(base):  # type: ignore[valid-type, misc]
        def seed(self, folder: Path, step: Any, active: Any, row: Any) -> Any:
            if self.parent is None:
                return build(folder, active[-1], row, vertices)
            return super().seed(folder, step, active, row)

    return InitialRootStages(root, meshes, frame)


def build(folder: Path, bone: Any, row: Any, vertices: int) -> Path:
    physical = worker.module("spherical_sequences_trial")
    geometry = worker.module("local_skin_seed")
    prepare(folder, bone, row, physical)
    row["padding"] = physical.call(
        [physical.NATIVE, "hull-seed", folder / "raw", folder], folder, "padding"
    )
    row["isotropic"] = isotropic(folder, vertices, physical)
    physical.audit_seed(folder, row)
    seed = folder / "seed"
    geometry.link_mesh(folder / "refined", seed)
    points = np.full((seed / "latest.bin").stat().st_size // 24, -1, dtype="<i4")
    faces = np.full((seed / "faces.bin").stat().st_size // 12, -1, dtype="<i4")
    geometry.ancestry(seed, points, faces)
    return seed


def prepare(folder: Path, bone: Any, row: Any, physical: Any) -> None:
    (folder / "references").mkdir(parents=True)
    physical.write_input(folder / "input.bin", [bone])
    shutil.copyfile(physical.NORMALIZATION, folder / "references/frame.bin")
    started = perf_counter()
    with closing(physical.ConvexHull(bone[0])) as hull:
        physical.capture_facets(hull, bone[0], folder / "raw")
    row["qhull_s"] = perf_counter() - started


def isotropic(folder: Path, vertices: int, physical: Any) -> Any:
    try:
        return physical.call(
            [physical.NATIVE, "sphere-isotropic", folder, folder, vertices], folder, "iso"
        )
    except RuntimeError as error:
        witness = containment_failure(folder, physical, error)
        physical.write(folder / "initial-containment-failure.json", witness)
    args = [physical.NATIVE, "sphere-isotropic-features", folder, folder, vertices]
    result = physical.call(args, folder, "iso-features")
    return dict(result, protected_sharp_edges=True, initial_witness=witness)


def containment_failure(folder: Path, physical: Any, error: RuntimeError) -> Any:
    if "Invalid hull/reference:" not in str(error):
        raise error
    witness = physical.read(folder / "refined/validation.json")
    if not witness or witness["self"] or witness["degenerate"]:
        raise error
    # Native admission also checks minimum clearance, even with no outside/crossing faces.
    return witness
