"""Serial production shortcut profiles with exact geometry/attachment evidence."""

import json
import sys
from contextlib import closing
from pathlib import Path

from profiler_system_load import system_load, system_times
from qualify_retained_attachment_edits import load
from shortcut_inspection_profile import PLAN, edit, fingerprint

from anthroforge.application.session import Session
from anthroforge.profiling.identity import build_identity


def measure(session, case, output, recording):
    if recording:
        session.command("profile.start", seconds=120)
    started = system_times()
    edit(session, case)
    result = dict(load=system_load(started), errors=session.scheduler.errors)
    if recording:
        session.command("profile.stop", path=str(output.with_suffix(".afprofile.zip")), wait=True)
    return result


def run(output, case_name, recording=True):
    output.parent.mkdir(parents=True, exist_ok=True)
    plan = json.loads(PLAN.read_text())
    case = next(c for c in plan["cases"] if c["id"] == case_name)
    with closing(Session()) as session:
        load(session, Path(plan["standalone"]))
        before = fingerprint(session)
        result = measure(session, case, output, recording)
        result.update(before=before, after=fingerprint(session), case=case, build=build_identity())
        output.with_suffix(".json").write_text(json.dumps(result), encoding="utf-8")
        print(output.name, result["load"]["wall_seconds"], result["errors"], flush=True)


if __name__ == "__main__":
    run(Path(sys.argv[1]).resolve(), sys.argv[2], "--unrecorded" not in sys.argv)
