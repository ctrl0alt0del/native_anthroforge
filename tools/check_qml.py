"""Check registered panel APIs; retain full diagnostics for legacy dynamic QML data."""

import argparse
import json
import os
import re
import subprocess
from pathlib import Path

from qml_metadata import ROOT, generate


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qt", type=Path, default=ROOT / ".tools/qt/6.12.0/msvc2022_64")
    parser.add_argument("--output", type=Path, default=ROOT / "build/qml-check")
    parser.add_argument(
        "--native", type=Path, default=Path(os.getenv("AF_NATIVE_BUILD", ROOT / "build/dev"))
    )
    return parser.parse_args()


def lint(options, paths, name):
    report = options.output / f"{name}.json"
    command = [str(options.qt / "bin/qmllint.exe"), "--ignore-settings"]
    for path in (
        options.output / "qml",
        options.native / "qml",
        ROOT / "src/anthroforge/desktop/qml",
    ):
        command += ["-I", str(path)]
    process = subprocess.run(
        [*command, "--json", str(report), *map(str, paths)], capture_output=True, text=True
    )
    (options.output / f"{name}.log").write_text(process.stdout + process.stderr, encoding="utf-8")
    return json.loads(report.read_text(encoding="utf-8"))["files"]


def interface_failure(warning, names):
    message = warning["message"]
    types = set(re.findall(r'"([^"\n]+)"', message))
    if warning["id"] == "import" and "AnthroForge.Desktop" in message:
        return True
    return bool(types & names) or warning["type"] in {"error", "critical"}


def findings(files, names):
    return [
        (item["filename"], warning)
        for item in files
        for warning in item["warnings"]
        if interface_failure(warning, names)
    ]


def verify_negative_probe(options, names):
    probe = options.output / "InvalidApi.qml"
    probe.write_text(
        "import QtQuick\nimport AnthroForge.Desktop 1.0\n"
        "Item { property var invalid: App.selection.nonexistentAction() }\n",
        encoding="utf-8",
    )
    errors = findings(lint(options, [probe], "negative-probe"), names)
    if not any("nonexistentAction" in value[1]["message"] for value in errors):
        raise RuntimeError("QML interface check failed to detect an invalid registered method.")


def main():
    options = arguments()
    names = generate(options.qt, options.output)
    verify_negative_probe(options, names)
    paths = sorted((ROOT / "src/anthroforge/desktop/qml").glob("*.qml"))
    files = lint(options, paths, "diagnostics")
    failures = findings(files, names)
    for path, warning in failures:
        print(f"{path}:{warning['line']}: {warning['message']}")
    print(
        f"Checked {len(paths)} QML files / {len(names)} registered model types; {len(failures)} API errors."
    )
    print(f"Full diagnostics (including dynamic state and legacy QML warnings): {options.output}")
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
