"""Reproducible UI dispatch inventory; static coverage is not behavioral acceptance."""

import ast
import json
import re
from pathlib import Path

from anthroforge.application import commands

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "build/authoring-parity-043"
SINGLE = {"begin", "commit", "cancel", "undo", "redo", "evaluate", "import", "update_mode"}


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
    rows = [row for file in desktop.rglob("*.py") for row in python_calls(file, names)]
    rows += [row for file in (desktop / "qml").glob("*.qml") for row in qml_calls(file, names)]
    return dict(
        registered_operations=sorted(names),
        literal_ui_calls=rows,
        missing_literal_operations=[r for r in rows if not r["registered"]],
        scope="Literal dispatch inventory only; dynamic composition/helpers require review.",
    )


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    result = inventory(set(commands.registered()))
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
