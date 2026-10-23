"""Canonical executable parity for the approved Humerus shortcut correction."""

import json
import sys
from contextlib import closing
from pathlib import Path

from check_migrated_shortcuts_portable import desktop_capture
from check_portable import invoke
from check_retained_attachments_portable import commands, render_assembly
from probe_ribs_ulna_latency import geometry
from qualify_retained_attachment_edits import load
from ribs_ulna_equivalence import attachments
from shortcut_parity_plan import read, write

from anthroforge.application.session import Session


def batch(evidence):
    plan = read(evidence / "plan.json")
    case = next(c for c in plan["cases"] if c["id"] == "SHORTCUT_15")
    requests = commands(Path(plan["standalone"]), dict(case["mapping"], value=case["value"] / 1.05))
    requests[3]["arguments"]["value"] = case["value"]
    return requests


def fingerprints(path):
    with closing(Session()) as session:
        load(session, path)
        assert not session.scheduler.errors
        return dict(geometry=geometry(session), attachments=attachments(session))


def verify(evidence, output):
    expected = fingerprints(evidence / "humerus-edited.anthroforge")
    for name in ("edited.anthroforge", "roundtrip.anthroforge"):
        actual = fingerprints(output / name)
        assert actual == expected, name
    write(
        output / "equivalence.json",
        dict(
            geometry_count=len(expected["geometry"]),
            attachment_count=len(expected["attachments"]),
            exact=True,
            baseline=str(evidence / "humerus-edited.anthroforge"),
        ),
    )


def run(executable, evidence, output):
    output.mkdir(parents=True, exist_ok=True)
    write(output / "commands.json", batch(evidence))
    result = invoke(
        executable, output, "--cli", "run", str(output / "commands.json"), background=True
    )
    (output / "headless.jsonl").write_text(result, encoding="utf-8")
    assert all(json.loads(line)["ok"] for line in result.splitlines())
    verify(evidence, output)
    desktop_capture(executable, output)
    render_assembly(executable, output)
    print(
        "Packaged Humerus edit/history/reopen, exact geometry/bindings and hidden rendering passed."
    )


if __name__ == "__main__":
    run(*(Path(value).resolve() for value in sys.argv[1:4]))
