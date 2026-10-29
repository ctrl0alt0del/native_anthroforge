"""Reconstruction acceptance on the saved production assembly; source is read-only."""

import hashlib
import json
import sys
from contextlib import closing
from pathlib import Path
from time import perf_counter

import psutil
import skeleton_update_qualification as fidelity

from anthroforge.application import storage
from anthroforge.application.session import Session

OUTPUT = Path("build/reconstruction-042/production")
SCM = "fc8df927-2290-4af2-b8e9-882697a8733e"


def report(name, value):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / (name + ".json")).write_text(json.dumps(value, indent=2), "utf-8")
    print(name, json.dumps(value)[:1200], flush=True)


def measure(label, function, *args, **kwargs):
    started = perf_counter()
    result = function(*args, **kwargs)
    report(
        label,
        dict(seconds=perf_counter() - started, memory=psutil.Process().memory_info()._asdict()),
    )
    return result


def promote(session, key):
    session.command("variant.review.prepare", variant=key)
    state = session.command("variant.review.status", wait=True, timeout=1800)
    report("review", state)
    assert state["state"] == "ready" and state["ready"], state
    candidate = session.variant_review.runtime.preparation.candidate
    apply_candidate(session, candidate, state)


def apply_candidate(session, candidate, state):
    expected = fidelity.candidate_context(session, candidate)
    approved = [f["key"] for f in state["findings"] if f["acknowledge"]]
    measure(
        "promotion",
        session.command,
        "variant.review.apply",
        token=state["token"],
        approved=approved,
    )
    session.wait(1800)
    delta = fidelity.compare(expected, session, {})
    report("preview-commit", delta)
    assert not delta, delta


def alternatives(session):
    before = fidelity.snapshot(session)
    row = measure("create", session.command, "variant.create", subjects=[SCM], name="SCM thickness")
    session.command("tissue.inflation", target=SCM, changes=dict(amount=0.018))
    measure("variant-evaluation", session.wait, 1800)
    checkpoint = session.command("variant.checkpoint", name="Thickness review")["id"]
    session.command("variant.fork", variant=checkpoint, name="Second alternative", enter=False)
    session.command("variant.leave")
    assert not fidelity.compare(before, session, {}), "Alternative modified accepted anatomy"
    measure("prepare-and-promote", promote, session, row["id"])
    return before


def persistence(session, before):
    path = OUTPUT / "reconstruction.anthroforge"
    measure("save", session.command, "save", path=str(path), blocked_policy="wait")
    document, resources = measure("reopen", storage.read_package, path, session.engine)
    reopened = fidelity.candidate_context(
        session, type("Candidate", (), dict(document=document, resources=resources))
    )
    assert not fidelity.compare(session, reopened, {}), "Reopened geometry changed"
    session.command("undo")
    session.wait(1800)
    differences = fidelity.compare(before, session, {})
    report("undo", differences)
    assert not differences, differences


def run(source):
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    with closing(Session("Reconstruction qualification")) as session:
        measure("open", session.command, "open", path=str(source))
        session.wait(600)
        session.command("profile.start", seconds=1800, memory_mib=256)
        before = alternatives(session)
        persistence(session, before)
        session.command(
            "profile.stop", path=str((OUTPUT / "workflow.afprofile.zip").resolve()), wait=True
        )
    assert hashlib.sha256(source.read_bytes()).hexdigest() == digest
    report("source-integrity", dict(sha256=digest, unchanged=True))


if __name__ == "__main__":
    run(Path(sys.argv[1]))
