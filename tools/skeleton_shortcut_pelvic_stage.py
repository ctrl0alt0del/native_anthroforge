"""Integrate retained body shaping and attachment override intent into the assembly."""

import json
import sys
from contextlib import closing
from pathlib import Path

from skeleton_shortcut_guides import settled
from skeleton_shortcut_pelvis import migrate, policies

from anthroforge.application.session import Session


def configure(session, mappings, frames, definitions):
    session.begin()
    preserve_independent_counterparts(session)
    migrate(session, mappings, frames)
    policies(session, mappings, definitions)
    session.commit()
    settled(session)
    assert not session.scheduler.errors, session.scheduler.errors
    failures = [r.error for r in session.document.formula_results if r.status != "ready"]
    assert not failures, failures


def preserve_independent_counterparts(session):
    # Retire the unqualified radius checkpoint's extra mirror outputs, if present.
    for driver in tuple(session.document.driving_shortcuts):
        for formula in driver.formulas:
            if formula.target.target == "pelvic-guide:mirror":
                session.command("driver.formula.remove", driver=driver.id, formula=formula.id)


def run(folder):
    mappings = json.loads((folder / "radius-mapping.json").read_text(encoding="utf-8"))
    frames = json.loads((folder / "donor-frames.json").read_text(encoding="utf-8"))
    definitions = json.loads((folder / "donor-definitions.json").read_text(encoding="utf-8"))
    with closing(Session()) as session:
        session.command("open", path=str(folder / "radius-checkpoint.anthroforge"))
        settled(session)
        configure(session, mappings, frames, definitions)
        session.command(
            "save", path=str(folder / "pelvic-checkpoint.anthroforge"), blocked_policy="wait"
        )
    (folder / "complete-mapping.json").write_text(json.dumps(mappings, indent=2), encoding="utf-8")


if __name__ == "__main__":
    run(Path(sys.argv[1]))
