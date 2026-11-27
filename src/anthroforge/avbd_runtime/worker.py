"""Owned checkpoint orchestration around the installed, unchanged numerical runtime."""

import argparse
import importlib
import json
import sys
from functools import cache
from pathlib import Path
from typing import Any

from . import bones, tissues


@cache
def module(name: str) -> Any:
    return importlib.import_module("tools.runtime.skin." + name)


def write(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, allow_nan=False), encoding="utf-8")


def read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runtime", type=Path)
    parser.add_argument("folder", type=Path)
    return execute(parser.parse_args())


def execute(args: Any) -> int:
    sys.path.insert(0, str(args.runtime))
    recipe = module("skin_recipe").load(args.folder / "recipe.json", args.folder)
    module("skin_experiment").configure(recipe.frame)
    output = args.folder / "output"
    output.mkdir()
    try:
        module("skin_tissue_run").preflight(recipe.muscles)
        skeleton = bones.run(recipe, output, read(args.folder / "resume.json"))
        skin = tissues.run(skeleton, recipe, output, read(args.folder / "resume.json"))
        write(output / "result.json", dict(accepted=True, skin=str(skin)))
        return 0
    except Exception as error:
        write(output / "result.json", dict(accepted=False, error=str(error)))
        return 1


def receipt(output: Path, kind: str, index: int, files: Any, state: Any) -> None:
    path = output / "checkpoints.json"
    records = read(path) if path.exists() else []
    owned = {key: str(value.relative_to(output)) for key, value in files.items()}
    records.append(dict(kind=kind, index=index, files=owned, state=state))
    write(path, records)
