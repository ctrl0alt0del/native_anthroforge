"""Qualify the real shortcut edit/history and saved geometry in the canonical executable."""

import json
import sys
from contextlib import closing
from pathlib import Path

from check_migrated_shortcuts_portable import desktop_capture, request
from check_portable import invoke
from check_retained_attachments_portable import render_assembly, roundtrip
from probe_ribs_ulna_latency import geometry
from qualify_retained_attachment_edits import load
from ribs_ulna_equivalence import attachments

from anthroforge.application.session import Session

DRIVER = "95809822-bcd3-4dfe-8985-6980772eb699"


def commands(source):
    return [
        request("open", path=str(source)),
        request("wait"),
        request("profile.start"),
        request("driver.value", driver=DRIVER, value=3.0),
        request("wait"),
        request("profile.stop", path="edit.afprofile.zip", wait=True),
        request("undo"),
        request("wait"),
        request("redo"),
        request("wait"),
        *roundtrip(),
    ]


def verify(output, expected):
    with closing(Session()) as session:
        load(session, output / "roundtrip.anthroforge")
        assert geometry(session) == json.loads((expected / "geometry.json").read_text())
        assert attachments(session) == json.loads((expected / "attachments.json").read_text())
        assert not session.scheduler.errors


def run(executable, source, expected, output):
    output.mkdir(parents=True, exist_ok=True)
    batch = output / "commands.json"
    batch.write_text(json.dumps(commands(source)), encoding="utf-8")
    result = invoke(executable, output, "--cli", "run", str(batch), background=True)
    (output / "headless.jsonl").write_text(result, encoding="utf-8")
    assert all(json.loads(line)["ok"] for line in result.splitlines())
    verify(output, expected)
    desktop_capture(executable, output)
    render_assembly(executable, output)
    print("Ribs=3, undo/redo, reopen, geometry/attachments and hidden desktop/render passed.")


if __name__ == "__main__":
    run(*(Path(value).resolve() for value in sys.argv[1:5]))
