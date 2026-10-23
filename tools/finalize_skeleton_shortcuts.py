"""Save the verified baseline with source-ordered exposed controls, without editing inputs."""

import json
import sys
from contextlib import closing
from pathlib import Path

from skeleton_shortcut_guides import settled
from skeleton_shortcut_migration import digest

from anthroforge.application.session import Session
from anthroforge.core.fibers import Fiber
from anthroforge.core.tissues import TissueVCP

NAME = "skeleton_96_muscles_shortcuts_v001.anthroforge"


def source_order(session, definitions, mappings):
    rows = definitions["roots"]["AF_ROOT"]["shortcuts"]
    order = [mappings[r["id"]].get("wrapper", mappings[r["id"]].get("driver")) for r in rows]
    all_keys = [s.id for s in (*session.document.shortcuts, *session.document.driving_shortcuts)]
    session.command("shortcut.reorder", identities=order + [k for k in all_keys if k not in order])
    shown = session.command("shortcut.list")
    assert len(shown) == 105 and [s["id"] for s in shown] == order


def verify(session):
    assert not session.scheduler.errors, session.scheduler.errors
    assert not session.document.shortcut_edits
    assert all(r.status == "ready" for r in session.document.formula_results)
    tissues = [o for o in session.document.objects if isinstance(o, TissueVCP)]
    assert len(tissues) == 96 and all(o.result.status == "ready" for o in tissues)
    return dict(
        scps=len(session.document.entities),
        tissues=len(tissues),
        fibers=sum(isinstance(o, Fiber) for o in session.document.objects),
        controls=len(session.document.controls),
        shortcuts=105,
        formulas=len(session.document.formula_results),
        revision=session.document.revision,
    )


def run(folder):
    mappings = json.loads((folder / "compact-mapping.json").read_text())
    definitions = json.loads((folder / "donor-definitions.json").read_text())
    before = digest(folder / "input.anthroforge")
    with closing(Session()) as session:
        session.command("open", path=str(folder / "compact-checkpoint.anthroforge"))
        settled(session)
        source_order(session, definitions, mappings)
        report = verify(session)
        session.command("save", path=str(folder / NAME), blocked_policy="wait")
    assert digest(folder / "input.anthroforge") == before
    report.update(input_sha256=before, output_sha256=digest(folder / NAME), file=str(folder / NAME))
    (folder / "delivery.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report))


if __name__ == "__main__":
    run(Path(sys.argv[1]))
