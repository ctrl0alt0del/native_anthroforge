"""Bounded inspection of actual queued dependencies during a migrated shortcut edit."""

import json
import sys
from contextlib import closing
from pathlib import Path

from skeleton_shortcut_exercise import edit

from anthroforge.application import dependencies
from anthroforge.application.session import Session


def record(session, job):
    return dict(
        id=job.id,
        kind=job.kind,
        label=job.label,
        state=job.state,
        outputs=sorted(job.outputs),
        provides=[str(p) for p in job.provides],
        blockers=blockers(session, job),
    )


def blockers(session, job):
    blockers = [b for b in session.scheduler.blockers(job) if blocks(b, job)]
    return [
        dict(
            id=b.id,
            label=b.label,
            kind=b.kind,
            ports=[str(p) for p in b.provides & job.prerequisites],
        )
        for b in blockers
    ]


def blocks(candidate, job):
    return candidate.id != job.id and (
        candidate.provides & job.prerequisites
        or candidate.future
        and candidate.outputs & job.outputs
    )


def capture(session, folder):
    rows = [record(session, j) for j in session.scheduler.active_jobs]
    document = session.document
    result = dict(
        jobs=rows,
        cycles=[list(map(str, c)) for c in dependencies.graph(document).cycles],
        formulas=[(r.formula, r.status, r.error) for r in document.formula_results],
        contexts=[(c.id, c.status, c.error) for c in document.shortcut_edits],
    )
    (folder / "wait-diagnostic.json").write_text(json.dumps(result, indent=2))
    selected = [r for r in rows if r["kind"] in ("formulas", "attachments", "shortcut_capture")]
    print(json.dumps(selected, indent=2))


def run(folder, number):
    mapping = json.loads((folder / "compact-mapping.json").read_text())["SHORTCUT_" + number]
    with closing(Session()) as session:
        session.command("open", path=str(folder / "compact-checkpoint.anthroforge"))
        session.wait(120)
        edit(session, mapping)
        try:
            session.wait(20)
        except TimeoutError:
            capture(session, folder)


if __name__ == "__main__":
    run(Path(sys.argv[1]), sys.argv[2])
