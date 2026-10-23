"""Integrate retained body shaping and attachment override intent into the assembly."""

import json
import sys
from contextlib import closing
from pathlib import Path

from skeleton_shortcut_batch import FormulaBatch
from skeleton_shortcut_guides import settled
from skeleton_shortcut_pelvis import migrate, policies

from anthroforge.application.session import Session


def configure(session, mappings, frames, definitions, compact=False):
    session.begin()
    preserve_independent_counterparts(session)
    batch = FormulaBatch(session)
    migrate_definition(batch, mappings, frames, compact)
    batch.flush()
    policies(session, mappings, definitions)
    diagnose_cycles(session)
    session.commit()
    settled(session)
    assert not session.scheduler.errors, session.scheduler.errors
    failures = [r.error for r in session.document.formula_results if r.status != "ready"]
    assert not failures, failures


def migrate_definition(batch, mappings, frames, compact):
    if compact:
        from skeleton_shortcut_pelvic_hooks import migrate as compact_migrate

        compact_migrate(batch, mappings, frames)
    else:
        migrate(batch, mappings, frames)


def diagnose_cycles(session):
    from anthroforge.application.dependencies import graph

    records = session.document.formula_index.formulas
    for cycle in graph(session.document).cycles:
        rows = [
            (records[p.owner][0].label, records[p.owner][1].target)
            if p.owner in records
            else (p.owner, p.output)
            for p in cycle
        ]
        print("Cycle:", rows, flush=True)
    assert not graph(session.document).cycles, "Migration authored a dependency cycle."


def preserve_independent_counterparts(session):
    # Retire the unqualified radius checkpoint's extra mirror outputs, if present.
    for driver in tuple(session.document.driving_shortcuts):
        for formula in driver.formulas:
            if formula.target.target == "pelvic-guide:mirror":
                session.command("driver.formula.remove", driver=driver.id, formula=formula.id)


def run(folder, compact=False):
    mappings = json.loads((folder / "radius-mapping.json").read_text(encoding="utf-8"))
    frames = json.loads((folder / "donor-frames.json").read_text(encoding="utf-8"))
    definitions = json.loads((folder / "donor-definitions.json").read_text(encoding="utf-8"))
    output = "compact-checkpoint.anthroforge" if compact else "pelvic-checkpoint.anthroforge"
    with closing(Session()) as session:
        session.command("open", path=str(folder / "radius-checkpoint.anthroforge"))
        settled(session)
        configure(session, mappings, frames, definitions, compact)
        session.command("save", path=str(folder / output), blocked_policy="wait")
    name = "compact-mapping.json" if compact else "complete-mapping.json"
    (folder / name).write_text(json.dumps(mappings, indent=2), encoding="utf-8")


if __name__ == "__main__":
    run(Path(sys.argv[1]), "--compact" in sys.argv)
