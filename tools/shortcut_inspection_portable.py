"""Inspect compiled desktop adapters through a relocated, offscreen QML test harness."""

import json
import shutil
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile

from check_portable import clean_environment

HARNESS = """
    Timer {
        interval: 500; running: true
        onTriggered: {
            inspectorHeader.shortcuts=true;
            workspace.shortcutPanel.editing.select(SHORTCUT_ID);
            workspace.shortcutPanel.editing.inspectionView.activate(true);
            workspace.shortcutPanel.editing.inspectionView.showEffects(true);
        }
    }
    Timer {
        interval: 1500; running: true
        onTriggered: console.log("AF_INSPECTION="+JSON.stringify(
            workspace.shortcutPanel.editing.inspectionView.state))
    }
"""


def prepare(distribution, project, output, template=HARNESS):
    target = output / "application"
    shutil.copytree(distribution, target, dirs_exist_ok=True)
    with ZipFile(project) as archive:
        document = json.loads(archive.read("manifest.json"))["document"]
    key = document["driving_shortcuts"][0]["id"]
    path = target / "anthroforge/desktop/qml/Main.qml"
    harness = template.replace("SHORTCUT_ID", json.dumps(key))
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("    id: window", "    id: window\n" + harness), encoding="utf-8")
    return target / "AnthroForge.exe"


def launch(executable, project, output):
    environment = clean_environment(background=True)
    environment["QT_FORCE_STDERR_LOGGING"] = "1"
    environment["ANTHROFORGE_PREFERENCES_PATH"] = str(output / "preferences.json")
    result = subprocess.run(
        arguments(executable, project, output),
        cwd=output,
        env=environment,
        capture_output=True,
        text=True,
        timeout=90,
    )
    (output / "desktop.log").write_text(result.stdout + result.stderr, encoding="utf-8")
    assert result.returncode == 0, result.stdout + result.stderr
    return result


def arguments(executable, project, output):
    return [
        str(executable),
        "--project",
        str(project),
        "--smoke-test",
        "--screenshot",
        str(output / "packaged-inspection.png"),
    ]


def verify(result, output):
    smoke = json.loads(result.stdout.strip())
    assert smoke["desktop_smoke"] and not smoke["warnings"], smoke
    line = next(
        row.split("AF_INSPECTION=", 1)[1]
        for row in result.stderr.splitlines()
        if "AF_INSPECTION=" in row
    )
    state = json.loads(line)
    assert state["showEffects"] and state["total"] > 0 and state["formulas"], state
    assert state["progress"]["state"] == "complete", state
    report = dict(passed=True, interactive=False, relocated=True, state=state, smoke=smoke)
    (output / "packaged-inspection.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(dict(passed=True, interactive=False, relocated=True)))


def main(distribution, project, output):
    output.mkdir(parents=True, exist_ok=True)
    executable = prepare(distribution, project, output)
    verify(launch(executable, project, output), output)


if __name__ == "__main__":
    main(*(Path(argument).resolve() for argument in sys.argv[1:4]))
