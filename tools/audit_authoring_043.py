"""Reproducible UI dispatch inventory; static coverage is not behavioral acceptance."""

import ast
import inspect
import json
import re
from contextlib import closing
from importlib import import_module
from pathlib import Path

from anthroforge.application import commands, inspection_commands, shortcut_inspection
from anthroforge.application import tissue_inspection as tissue
from anthroforge.application.issues.commands import catalogue
from anthroforge.application.session import Session

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "build/authoring-parity-043"
SINGLE = {"begin", "commit", "cancel", "undo", "redo", "evaluate", "import", "update_mode"}
EXTRA = {
    "variant_operations": ("variant.", "operations_table"),
    "catalogue_operations": ("catalogue.", "operations"),
    "reconstruction_reviews": ("", ""),
    "reconstruction_queue": ("reconstruction.queue.", ""),
    "reconstruction_evidence": ("reconstruction.evidence.", ""),
    "reconstruction_stages": ("reconstruction.stage.", ""),
    "reconstruction_comparison": ("reconstruction.compare.", ""),
}


def operation_names(session):
    tables = [commands.EDITS, commands.direct_commands(session), catalogue(session)]
    tables += [inspection_commands.OPERATIONS, shortcut_inspection.operations()]
    tables += [tissue.operations(session), tissue.route_operations(session)]
    tables += [tissue.skin_operations(session)]
    names = set().union(*(table.keys() for table in tables))
    names.update(("property.discover", "property.get", "shortcut.inspect", "shortcut.list"))
    names.update("profile." + key for key in ("start", "status", "stop"))
    names.update("variant.review." + key for key in ("prepare", "status", "apply", "cancel"))
    names.add("catalogue.collection.remove")
    return names | reconstruction_names()


def reconstruction_names():
    names = set()
    for module, (prefix, provider) in EXTRA.items():
        owner = import_module("anthroforge.application." + module)
        keys = getattr(owner, provider)() if provider else literal_dispatch(owner.execute)
        names.update(prefix + key for key in keys)
    return names


def literal_dispatch(function):
    tree = ast.parse(inspect.getsource(function))
    keys = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            keys.update(k.value for k in node.keys if isinstance(k, ast.Constant))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "dict":
                keys.update(k.arg for k in node.keywords if k.arg)
    return keys


def candidates(value, names):
    return value in names or value in SINGLE or bool(re.fullmatch(r"[a-z_]+\.[a-z_.]+", value))


def python_calls(path, names):
    tree = ast.parse(path.read_text("utf-8"))
    rows = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr not in {"run", "command", "edit", "setting"} or not node.args:
            continue
        values = [v.value for v in ast.walk(node.args[0]) if isinstance(v, ast.Constant)]
        rows += [
            record(path, node.lineno, v, names)
            for v in values
            if isinstance(v, str) and candidates(v, names)
        ]
    return rows


def qml_calls(path, names):
    pattern = re.compile(r'(?:run|command|edit|setting)\(\s*["\x27]([^"\x27]+)')
    return [
        record(path, number, match.group(1), names)
        for number, line in enumerate(path.read_text("utf-8").splitlines(), 1)
        for match in pattern.finditer(line)
        if candidates(match.group(1), names)
    ]


def record(path, line, operation, names):
    return dict(
        file=path.relative_to(ROOT).as_posix(),
        line=line,
        operation=operation,
        registered=operation in names,
    )


def inventory(names):
    desktop = ROOT / "src/anthroforge/desktop"
    rows = [row for file in desktop.glob("*.py") for row in python_calls(file, names)]
    rows += [row for file in (desktop / "qml").glob("*.qml") for row in qml_calls(file, names)]
    return dict(
        registered_operations=sorted(names),
        literal_ui_calls=rows,
        missing_literal_operations=[r for r in rows if not r["registered"]],
        scope="Literal dispatch inventory only; dynamic composition/helpers require review.",
    )


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with closing(Session()) as session:
        result = inventory(operation_names(session))
    (OUTPUT / "dispatch-inventory.json").write_text(json.dumps(result, indent=2), "utf-8")
    print(
        json.dumps(
            dict(
                registered=len(result["registered_operations"]),
                ui_calls=len(result["literal_ui_calls"]),
                missing=result["missing_literal_operations"],
            )
        )
    )


if __name__ == "__main__":
    main()
