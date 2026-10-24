"""Comparison capture, real paired rendering and isolated replay in the shipped executable."""

import json
from zipfile import ZipFile

from shortcuts_portable import consumer_requests, request


def comparison(executable, cwd, invoke):
    commands = json.loads((cwd / "examples/shortcuts_parametric.json").read_text())
    commands = [r for r in commands if r["operation"] != "save"]
    commands.extend(consumer_requests())
    commands.extend(comparison_requests())
    (cwd / "comparison.json").write_text(json.dumps(commands))
    output = invoke(executable, cwd, "--cli", "run", "comparison.json")
    rows = [json.loads(row) for row in output.splitlines() if row.startswith("{")]
    assert rows and all(row["ok"] for row in rows), rows
    with ZipFile(cwd / "comparison.afinspection.zip") as archive:
        data = json.loads(archive.read("inspection.json"))["comparison"]
        assert data["differences"]["changed"] > 0 and data["replay"]["complete"]
        assert {"before.png", "image.png", "starting.anthroforge"} <= set(archive.namelist())
    assert (cwd / "replayed.anthroforge").is_file()


def comparison_requests():
    return [
        request("workspace.update", camera=[0, 0, 0, 70, 0, 0, 0.25], orthographic=True),
        request("shortcut.comparison.capture", shortcut="$radius_driver"),
        request("driver.value", driver="$radius_driver", value=0.07),
        request("wait"),
        request("shortcut.comparison.inspect", wait=True),
        request("inspection.export", path="comparison.afinspection.zip", replay=True, wait=True),
        request(
            "inspection.replay", path="comparison.afinspection.zip", output="replayed.anthroforge"
        ),
        request("shortcut.comparison.clear"),
    ]
