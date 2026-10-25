"""Profile recovery of the production assembly and compare every serialized payload."""

import argparse
import json
import sys
from pathlib import Path
from time import monotonic, sleep
from zipfile import ZipFile

from anthroforge.application.autosave import Autosave
from anthroforge.application.preferences import PreferenceStore
from anthroforge.application.projects import adopt
from anthroforge.application.recovery import RecoveryStore
from anthroforge.application.session import Session
from anthroforge.application.storage import atomic_save, read_package


def compare(expected, recovered):
    with ZipFile(expected) as left, ZipFile(recovered) as right:
        names = left.namelist()
        assert set(names) == set(right.namelist()) - {"recovery.json"}
        for name in names:
            assert left.read(name) == right.read(name), name
    return len(names)


def record(session, saver, output):
    session.command("profile.start")
    saver.poll(session)
    saver.due = 0
    begin = monotonic()
    saver.poll(session)
    while saver.job is not None and monotonic() - begin < 120:
        session.scheduler.tick()
        sleep(0.005)
    elapsed = monotonic() - begin
    assert saver.last and saver.job is None and not saver.error, saver.error
    session.command("profile.stop", path=str(output / "autosave.afprofile.zip"), wait=True)
    return elapsed


def task_times(output):
    with ZipFile(output / "autosave.afprofile.zip") as archive:
        events = json.loads(archive.read("trace.json"))["traceEvents"]
    return {
        row["name"] + "_ms": row["dur"] / 1000
        for row in events
        if row["cat"] == "task" and row.get("ph") == "X"
    }


def exercise(session, source, output):
    adopt(session, *read_package(source, session.engine))
    session.saved_revision = -1
    before, cursor = session.document, session.history.cursor
    baseline = output / "expected.anthroforge"
    atomic_save(baseline, before, session.resources)
    saver = Autosave(RecoveryStore(output / "Autosaves"))
    elapsed = record(session, saver, output)
    recovered = Path(saver.last["path"])
    assert read_package(recovered, session.engine)[0] == before
    assert session.document is before and session.history.cursor == cursor
    report = report_result(before, elapsed, compare(baseline, recovered), output)
    (output / "acceptance.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report))


def report_result(document, elapsed, payloads, output):
    return dict(
        seconds=elapsed,
        payloads=payloads,
        **task_times(output),
        entities=len(document.entities),
        objects=len(document.objects),
        qt_free="PySide6" not in sys.modules,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, default=Path("build/usability-037/assembly"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    session = Session(preferences=PreferenceStore(None))
    try:
        exercise(session, args.source, args.output)
    finally:
        session.close()


if __name__ == "__main__":
    main()
