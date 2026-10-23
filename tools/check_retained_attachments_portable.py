"""Exercise the three reported attachment failures in the ordinary packaged executable."""

import json
import sys
import zipfile
from pathlib import Path

from check_migrated_shortcuts_portable import desktop_capture, request
from check_portable import invoke


def document(path):
    with zipfile.ZipFile(path) as archive:
        return json.loads(archive.read("manifest.json"))["document"]


def bindings(state):
    return {
        row["state"]["id"]: tuple(
            row["state"][key] for key in ("bindings", "attachment_asset", "supports")
        )
        for row in state["objects"]
        if row["kind"] == "fiber"
    }


def verify(path, expected):
    state = document(path)
    assert bindings(state) == expected, "Stored Fiber attachment intent changed."
    assert all(row["status"] == "ready" for row in state["entities"])
    results = [row["state"]["result"] for row in state["objects"]]
    assert all(row["status"] == "ready" for row in results), "An output is not ready."
    assert all(not row["pending"] and not row["error"] for row in results)


def commands(source, mapping):
    return [
        request("open", path=str(source)),
        request("wait"),
        request("profile.start"),
        request("shortcut.set", reference=mapping["reference"], value=mapping["value"] * 1.05),
        request("wait"),
        request("profile.stop", path="edit.afprofile.zip", wait=True),
        request("undo"),
        request("wait"),
        request("redo"),
        request("wait"),
        *roundtrip(),
    ]


def roundtrip():
    return [
        request("save", path="edited.anthroforge", blocked_policy="wait"),
        request("open", path="edited.anthroforge"),
        request("wait"),
        request("save", path="roundtrip.anthroforge", blocked_policy="wait"),
    ]


def exercise(executable, source, output, mapping, expected):
    output.mkdir(parents=True, exist_ok=True)
    batch = output / "commands.json"
    batch.write_text(json.dumps(commands(source, mapping)), encoding="utf-8")
    result = invoke(executable, output, "--cli", "run", str(batch), background=True)
    (output / "headless.jsonl").write_text(result, encoding="utf-8")
    assert all(json.loads(line)["ok"] for line in result.splitlines())
    for name in ("edited.anthroforge", "roundtrip.anthroforge"):
        verify(output / name, expected)


def render_assembly(executable, output):
    project, image = output / "roundtrip.anthroforge", output / "rendered.png"
    revision = document(project)["revision"]
    arguments = ("--cli", "render", str(project), str(image), "--revision", str(revision))
    result = invoke(executable, output, *arguments, background=True)
    assert json.loads(result)["captured"], result
    metadata = json.loads(image.with_suffix(".png.json").read_text())
    assert not metadata["window_visible"] and metadata["scene"]["vertices"] > 10000


def run(executable, source, mappings, output):
    data, expected = json.loads(mappings.read_text()), bindings(document(source))
    for number in (15, 16, 21):
        target = output / str(number)
        exercise(executable, source, target, data[f"SHORTCUT_{number}"], expected)
        print(
            f"Packaged control {number}: edit, undo/redo, reopen and bindings passed.", flush=True
        )
    desktop_capture(executable, output / "21")
    render_assembly(executable, output / "21")
    print("Hidden desktop opened the edited assembly; no native-window interaction claimed.")


if __name__ == "__main__":
    run(*(Path(value).resolve() for value in sys.argv[1:5]))
