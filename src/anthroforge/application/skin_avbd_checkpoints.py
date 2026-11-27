"""Capture portable checkpoint resources before the worker directory is released."""

import json
from dataclasses import replace
from pathlib import Path
from typing import Any

from anthroforge.core.skin_checkpoints import Checkpoint, matching

from . import skin_avbd_identity as identity
from . import skin_checkpoint_assets as assets

VERSION = 3


def prepare(folder: Path, request: Any, root: Path) -> tuple[Any, ...]:
    prefixes = identity.prefixes(folder, identity.runtime(root))
    records = request.document.skin.checkpoints
    skeletal = matching(records, prefixes[0], "AVBD", VERSION)
    tissue = latest_tissue(records, prefixes[1]) if len(skeletal) == len(prefixes[0]) else None
    kept = (*skeletal, *((tissue,) if tissue else ()))
    resume = {}
    for row in (*skeletal[-1:], *((tissue,) if tissue else ())):
        path = folder / ("resume-" + row.kind)
        state = assets.restore(request.resources.skin[row.resource], path)
        resume[row.kind] = dict(folder=str(path), state=state)
    (folder / "resume.json").write_text(json.dumps(resume), encoding="utf-8")
    return prefixes, tuple(assets.Bundle(r, request.resources.skin[r.resource]) for r in kept)


def latest_tissue(records: Any, prefixes: tuple[str, ...]) -> Checkpoint | None:
    index = {
        r.prefix: r
        for r in records
        if r.builder == "AVBD" and r.version == VERSION and r.kind == "VCP"
    }
    return next((index[p] for p in reversed(prefixes) if p in index), None)


def collect(folder: Path, prepared: Any, accepted: bool) -> tuple[assets.Bundle, ...]:
    prefixes, kept = prepared
    path = folder / "output/checkpoints.json"
    rows = json.loads(path.read_text()) if path.is_file() else []
    recipe = json.loads((folder / "recipe.json").read_text())
    all_bundles = list(kept)
    for row in rows:
        all_bundles.append(bundle(folder / "output", row, prefixes, recipe))
    bones = {b.checkpoint.source: b for b in all_bundles if b.checkpoint.kind == "SCP"}
    tissues = [b for b in all_bundles if b.checkpoint.kind == "VCP"]
    return (*bones.values(), *tissue_retention(tissues, accepted))


def tissue_retention(bundles: Any, accepted: bool) -> tuple[assets.Bundle, ...]:
    if not bundles:
        return ()
    last = bundles[-1]
    if accepted:
        return (replace(last, checkpoint=replace(last.checkpoint, durable=True)),)
    durable = next((b for b in reversed(bundles) if b.checkpoint.durable), None)
    return (durable, last) if durable and durable != last else (last,)


def bundle(output: Path, row: Any, prefixes: Any, recipe: Any) -> assets.Bundle:
    kind, index = row["kind"], row["index"]
    if kind not in ("SCP", "VCP") or type(index) is not int or index < 0:
        raise ValueError("Invalid AVBD checkpoint receipt.")
    key, offset = ("bones", 0) if kind == "SCP" else ("muscles", 1)
    source, prefix = recipe[key][index]["id"], prefixes[offset][index]
    files = {name: owned_file(output, path).read_bytes() for name, path in row["files"].items()}
    asset = assets.create(files, row["state"])
    record = Checkpoint("AVBD", VERSION, kind, source, prefix, asset.digest, kind == "SCP")
    return assets.Bundle(record, asset)


def owned_file(output: Path, name: str) -> Path:
    path = (output / assets.relative_name(Path(name).as_posix())).resolve()
    if output.resolve() not in path.parents:
        raise ValueError("AVBD checkpoint escaped its owned run directory.")
    return path
