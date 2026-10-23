"""Actual 96-muscle delivery: packaged edit/undo, round trip and hidden desktop opening."""

import json
import sys
from pathlib import Path

from check_portable import invoke
from finalize_skeleton_shortcuts import NAME


def request(operation, **arguments):
    return dict(operation=operation, arguments=arguments)


def commands(folder, mapping):
    return [
        request("open", path=str(folder / NAME)),
        request("wait"),
        request("profile.start"),
        request("driver.value", driver=mapping["driver"], value=0.05),
        request("wait"),
        request("profile.stop", path="iliac-edit.afprofile.zip", wait=True),
        request("undo"),
        request("wait"),
        request("save", path="roundtrip.anthroforge", blocked_policy="wait"),
    ]


def run(executable, folder, output):
    output.mkdir(parents=True, exist_ok=True)
    mappings = json.loads((folder / "compact-mapping.json").read_text())
    batch = output / "exercise.json"
    batch.write_text(json.dumps(commands(folder, mappings["SHORTCUT_13"])))
    headless = invoke(executable, output, "--cli", "run", str(batch), background=True)
    (output / "headless.json").write_text(headless)
    desktop_capture(executable, output)
    print("Packaged real-assembly control edit, undo, save and hidden desktop passed.")


def desktop_capture(executable, output):
    desktop = invoke(
        executable,
        output,
        "--project",
        str(output / "roundtrip.anthroforge"),
        "--smoke-test",
        "--screenshot",
        str(output / "desktop.png"),
        background=True,
    )
    assert json.loads(desktop)["desktop_smoke"], desktop
    assert json.loads(desktop)["entities"] == 59, desktop
    (output / "desktop.json").write_text(desktop)


if __name__ == "__main__":
    run(*(Path(p).resolve() for p in sys.argv[1:4]))
