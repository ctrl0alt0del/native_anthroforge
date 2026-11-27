"""Optional AVBD runtime adapter. All mutable run state belongs to one worker job."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import numpy as np

from anthroforge.native import process

from . import skin_avbd_capture, skin_avbd_checkpoints, skin_avbd_runtime
from .skin_draft_build import CheckpointFailure, DraftOutput, DraftRequest


def runtime() -> tuple[Path, Path]:
    return skin_avbd_runtime.installed()


def execute(engine: Any, folder: Path, cancel: int, installed: tuple[Path, Path]) -> Path:
    root, python = installed
    output = folder / "output"
    bootstrap = Path(__file__).resolve().parents[1] / "avbd_runtime/bootstrap.py"
    args = (str(python), "-I", str(bootstrap), str(root), str(folder))
    log = folder / "worker.log"
    code = process.run(engine, process.Request(args, root, log), cancel)
    if code:
        raise ValueError(f"AVBD draft worker failed ({code}). {failure(output, log)}")
    return accepted_path(output)


def accepted_path(output: Path) -> Path:
    receipt = json.loads((output / "result.json").read_text(encoding="utf-8"))
    if receipt.get("accepted") is not True:
        raise ValueError("AVBD returned an unaccepted draft.")
    skin = Path(receipt["skin"]).resolve()
    if output.resolve() not in skin.parents:
        raise ValueError("AVBD returned a draft outside its run directory.")
    return skin


def failure(output: Path, log: Path) -> str:
    receipt = output / "result.json"
    if receipt.is_file():
        return str(json.loads(receipt.read_text(encoding="utf-8")).get("error", "Unknown failure"))
    with log.open("rb") as stream:
        stream.seek(max(0, log.stat().st_size - 1600))
        return stream.read().decode("utf-8", errors="replace").strip()


def mesh_from_output(engine: Any, skin: Path) -> Any:
    positions, faces = skin / "latest.bin", skin / "faces.bin"
    if positions.stat().st_size % 24 or faces.stat().st_size % 12:
        raise ValueError("Truncated AVBD draft surface.")
    points = np.fromfile(positions, "<f8").reshape(-1, 3)
    triangles = np.fromfile(faces, "<i4").reshape(-1, 3)
    if not len(points) or not len(triangles) or not np.isfinite(points).all():
        raise ValueError("Empty or nonfinite AVBD draft surface.")
    if triangles.min() < 0 or triangles.max() >= len(points):
        raise ValueError("Invalid AVBD draft triangle index.")
    return engine.create_mesh(points, triangles.ravel(), np.arange(0, triangles.size + 1, 3))


def build(request: DraftRequest) -> DraftOutput:
    installed = runtime()
    with TemporaryDirectory(prefix="afskin-") as tmp:
        folder = Path(tmp).resolve()
        skin_avbd_capture.stage(folder, request)
        prepared = skin_avbd_checkpoints.prepare(folder, request, installed[0])
        return run_build(request, folder, installed, prepared)


def run_build(request: DraftRequest, folder: Path, installed: Any, prepared: Any) -> DraftOutput:
    try:
        skin = execute(request.engine, folder, request.cancel, installed)
        mesh = mesh_from_output(request.engine, skin)
        evidence = stage_evidence(folder / "output")
    except Exception as error:
        checkpoints = skin_avbd_checkpoints.collect(folder, prepared, False)
        raise CheckpointFailure(error, checkpoints) from error
    unavailable = ["mesh_quality", "coverage", "source_intersections"]
    checkpoints = skin_avbd_checkpoints.collect(folder, prepared, True)
    return DraftOutput(
        mesh, dict(quality=dict(unavailable=unavailable), construction=evidence), checkpoints
    )


def stage_evidence(output: Path) -> dict[str, Any]:
    bones = json.loads((output / "bones/stages.json").read_text(encoding="utf-8"))
    tissues = output / "muscles/summary.json"
    tissue_log = json.loads(tissues.read_text(encoding="utf-8")) if tissues.is_file() else {}
    stages = tissue_log.get("stages", [])
    validate_stages(output, bones, stages, tissue_log)
    result: dict[str, Any] = dict(
        material="local-stvk-v1",
        bones=[{k: b[k] for k in ("entity", "frames")} for b in bones],
        muscles=[{k: m[k] for k in ("entity", "route", "frames")} for m in stages],
    )
    witness = Path(bones[0]["folder"]) / "initial-containment-failure.json"
    if witness.is_file():
        result["root_seed_repair"] = json.loads(witness.read_text())
    return result


def validate_stages(output: Path, bones: Any, muscles: Any, tissue_log: dict[str, Any]) -> None:
    recipe = json.loads((output.parent / "recipe.json").read_text(encoding="utf-8"))
    for name, receipt in (("bones", bones), ("muscles", muscles)):
        if [item["id"] for item in recipe[name]] != [item["entity"] for item in receipt]:
            raise ValueError(f"AVBD returned incomplete or out-of-order {name} stages.")
    if any(stage.get("material") != "local-stvk-v1" for stage in bones):
        raise ValueError("AVBD worker did not produce local-StVK material for every stage.")
    if muscles and (
        tissue_log.get("accepted") is not True
        or any(item.get("accepted") is not True for item in muscles)
    ):
        raise ValueError("AVBD returned unaccepted muscle stages.")
