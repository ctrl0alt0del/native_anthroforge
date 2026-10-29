"""Production support refresh, promotion and post-promotion shortcut parity."""

import gc
import hashlib
import json
import sys
from contextlib import closing
from pathlib import Path

import assembly_qualification as edits
import reconstruction_qualification as checks
import skeleton_update_qualification as fidelity

from anthroforge.application import projects
from anthroforge.application.editing_contexts import bare
from anthroforge.application.session import Session

OUTPUT = Path("build/reconstruction-042/followup")


def shortcut(session, case):
    edits.apply_edit(session, case["mapping"], {}, case["value"])
    session.wait(1800)


def candidate(session, key, mode):
    session.command("variant.review.prepare", variant=key, mode=mode)
    state = session.command("variant.review.status", wait=True, timeout=1800)
    checks.report(mode + "-review", state)
    assert state["state"] == "ready" and state["ready"], state
    return state


def refresh(session, key):
    before = fidelity.snapshot(session)
    state = candidate(session, key, "refresh")
    session.command("variant.review.apply", token=state["token"])
    session.wait(1800)
    assert not fidelity.compare(before, session, {}), "Support refresh changed accepted anatomy"
    current = next(r for r in session.command("variant.inspect")["variants"] if r["id"] == key)
    assert not current["outdated"], current


def control_trial(session, case):
    baseline = fidelity.snapshot(session)
    with closing(Session("Accepted-only comparison")) as control:
        projects.adopt(control, bare(baseline.document), baseline.resources.snapshot())
        checks.measure("shortcut-with-variants", shortcut, session, case)
        checks.measure("shortcut-accepted-only", shortcut, control, case)
        differences = fidelity.compare(control, session, {})
        checks.report("shortcut-parity", dict(case=case["id"], differences=differences))
        assert not differences, differences
    del baseline
    gc.collect()


def followup(session, plan):
    key = next(v.id for v in session.document.reconstruction.variants if v.name == "SCM thickness")
    case = next(c for c in plan["cases"] if c["label"] == "Ribs Top Radius")
    checks.measure("post-promotion-shortcut", control_trial, session, case)
    current = next(r for r in session.command("variant.inspect")["variants"] if r["id"] == key)
    assert current["outdated"], current
    checks.measure("support-refresh", refresh, session, key)
    checks.measure("second-promotion", checks.promote, session, key)
    checks.measure(
        "save",
        session.command,
        "save",
        path=str(OUTPUT / "refreshed.anthroforge"),
        blocked_policy="wait",
    )


def run(source, plan):
    checks.OUTPUT = OUTPUT
    OUTPUT.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    with closing(Session("Production reconstruction follow-up")) as session:
        session.command("open", path=str(source))
        session.wait(1800)
        session.command("profile.start", seconds=1800, memory_mib=256)
        followup(session, plan)
        session.command(
            "profile.stop", path=str((OUTPUT / "followup.afprofile.zip").resolve()), wait=True
        )
    assert hashlib.sha256(source.read_bytes()).hexdigest() == digest
    checks.report("source-integrity", dict(sha256=digest, unchanged=True))


if __name__ == "__main__":
    run(Path(sys.argv[1]), json.loads(Path(sys.argv[2]).read_text("utf-8")))
