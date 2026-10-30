"""Generate tooling metadata from the same explicitly registered Python QML models."""

import ast
import inspect
import json
import subprocess
import sys
from pathlib import Path

import PySide6
from PySide6.QtCore import QObject

from anthroforge.desktop.app_models import TYPES, App

ROOT = Path(__file__).resolve().parents[1]


def model_classes():
    return {
        base
        for model in (App, *TYPES)
        for base in model.__mro__
        if issubclass(base, QObject) and base.__module__.startswith("anthroforge.")
    }


def dump_input(source, output):
    tree = ast.parse(source.read_text(encoding="utf-8"))
    # Qt 6.12 metaobjectdump dereferences ImportFrom.module for `from . import x`.
    # This temporary AST is never executed; imports do not affect Qt declarations.
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module is None:
            node.module = "anthroforge"
    target = output / source.name
    target.write_text(ast.unparse(tree), encoding="utf-8")
    return str(target)


def dump(classes, output):
    sources = sorted({Path(inspect.getfile(model)) for model in classes})
    inputs = [dump_input(source, output) for source in sources]
    script = Path(PySide6.__file__).parent / "scripts/metaobjectdump.py"
    process = subprocess.run(
        [sys.executable, str(script), *inputs], capture_output=True, text=True, check=True
    )
    (output / "dump.log").write_text(process.stderr, encoding="utf-8")
    return json.loads(process.stdout)


def declarations(records, classes):
    names = {model.__name__ for model in classes}
    for record in records:
        record["classes"] = [item for item in record["classes"] if item["className"] in names]
        for item in record["classes"]:
            item["object"] = True
            if item["className"] != "App":
                item["classInfos"] = [
                    {"name": "QML.Element", "value": "Af" + item["className"]},
                    {"name": "QML.Creatable", "value": "false"},
                ]
    return records


def foreign_types(qt):
    modules = ("core", "qml", "quick", "gui")
    return ",".join(str(qt / f"metatypes/qt6{name}_metatypes.json") for name in modules)


def register(qt, output, module, raw):
    command = [str(qt / "bin/qmltyperegistrar.exe"), "--import-name", "AnthroForge.Desktop"]
    command += ["--major-version", "1", "--minor-version", "0"]
    command += ["--generate-qmltypes", str(module / "plugins.qmltypes")]
    command += ["--foreign-types", foreign_types(qt)]
    command += ["-o", str(output / "unused_registration.cpp"), str(raw)]
    process = subprocess.run(command, capture_output=True, text=True, check=True)
    (output / "registrar.log").write_text(process.stdout + process.stderr, encoding="utf-8")


def generate(qt, output):
    output.mkdir(parents=True, exist_ok=True)
    classes = model_classes()
    records = declarations(dump(classes, output), classes)
    raw = output / "metadata.json"
    raw.write_text(json.dumps(records, indent=2), encoding="utf-8")
    module = output / "qml/AnthroForge/Desktop"
    module.mkdir(parents=True, exist_ok=True)
    (module / "qmldir").write_text(
        "module AnthroForge.Desktop\ntypeinfo plugins.qmltypes\n", encoding="utf-8"
    )
    register(qt, output, module, raw)
    return {model.__name__ for model in classes}
