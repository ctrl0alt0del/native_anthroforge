"""Retain accepted VCP chains; complete prior chains can seed an appended suffix."""

import shutil
from pathlib import Path
from time import perf_counter
from typing import Any

from . import skin_avbd_worker as worker


def run(bones: Any, recipe: Any, output: Path, resume: Any) -> Path:
    if not recipe.muscles:
        return Path(bones.checkpoint().skin)
    root = output / "muscles"
    root.mkdir()
    chain = make_chain(tissue_inputs(bones, recipe), root, resume.get("VCP"))
    sequence = worker.module("vcp_default_sequence")
    for tissue in recipe.muscles[len(chain.stages) :]:
        sequence.add(root, tissue.name, chain)
        checkpoint(chain, output)
    sequence.finish(root, chain, perf_counter())
    return Path(chain.skin)


def tissue_inputs(bones: Any, recipe: Any) -> Any:
    skeleton = bones.checkpoint()
    skeleton.check()
    measure = worker.module("skin_passages").PassageMeasure(recipe.bones, bones.meshes)
    return worker.module("skin_tissue_inputs").TissueInputs(
        skeleton, {t.name: t for t in recipe.muscles}, measure
    )


def make_chain(inputs: Any, root: Path, record: Any) -> Any:
    cls = worker.module("vcp_default_sequence").Chain
    if record is None:
        return cls(inputs.skeleton.skin, inputs.measure(inputs.skeleton.skin), inputs=inputs)
    folder = root / ".resume"
    shutil.copytree(record["folder"], folder)
    state = record["state"]
    skin = folder / "skin"
    prior = {key: folder / "prior" / key for key in state["prior"]}
    rows = [dict(row, parent=str(skin), skin=str(skin)) for row in state["stages"]]
    return cls(skin, state["passages"], prior, rows, inputs)


def checkpoint(chain: Any, output: Path) -> None:
    files = {"skin/" + name: chain.skin / name for name in ("latest.bin", "faces.bin")}
    for key, folder in chain.prior.items():
        for name in ("collider.bin", "collider-bounds.json"):
            files[f"prior/{key}/{name}"] = folder / name
    rows = [{k: v for k, v in row.items() if k not in ("parent", "skin")} for row in chain.stages]
    state = dict(stages=rows, passages=chain.passages, prior=list(chain.prior))
    worker.receipt(output, "VCP", len(rows) - 1, files, state)
