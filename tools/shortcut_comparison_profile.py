"""Production comparison overhead and unchanged geometry/attachment evidence."""

import json
from contextlib import closing
from pathlib import Path
from time import perf_counter

from qualify_retained_attachment_edits import load
from shortcut_inspection_profile import PLAN, edit, fingerprint, shortcut_key

from anthroforge.application.session import Session

OUTPUT = Path("build/shortcut-comparison-profile")


def run(case, project):
    with closing(Session()) as session:
        load(session, project)
        before = fingerprint(session)
        session.command("profile.start", seconds=120)
        start = perf_counter()
        session.command("shortcut.comparison.capture", shortcut=shortcut_key(case))
        capture_ms = (perf_counter() - start) * 1000
        start = perf_counter()
        edit(session, case)
        elapsed = perf_counter() - start
        finish(session, case, before, capture_ms, elapsed)


def finish(session, case, before, capture_ms, elapsed):
    start = perf_counter()
    comparison = session.command("shortcut.comparison.inspect", wait=True)
    comparison_ms = (perf_counter() - start) * 1000
    output = OUTPUT / case["id"]
    session.command("profile.stop", path=str(output.with_suffix(".afprofile.zip")), wait=True)
    result = dict(before=before, after=fingerprint(session), comparison=comparison)
    result.update(
        capture_ms=capture_ms,
        comparison_ms=comparison_ms,
        edit_seconds=elapsed,
        errors=session.scheduler.errors,
    )
    output.with_suffix(".json").write_text(json.dumps(result), "utf-8")
    print(case["id"], capture_ms, comparison_ms, elapsed, flush=True)


if __name__ == "__main__":
    OUTPUT.mkdir(parents=True, exist_ok=True)
    plan = json.loads(PLAN.read_text())
    for case in plan["cases"]:
        run(case, Path(plan["standalone"]))
