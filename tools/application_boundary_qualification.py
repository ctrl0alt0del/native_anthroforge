"""Repeatable command-dispatch microbenchmark and context lifetime checks."""

import gc
import json
import statistics
import sys
import weakref
from pathlib import Path
from time import perf_counter

from anthroforge.application.session import Session
from anthroforge.core.document import Document


def dispatch(session, count=10000):
    expected = session.command("preferences.get")
    start = perf_counter()
    for _ in range(count):
        value = session.command("preferences.get")
    assert value == expected
    return (perf_counter() - start) * 1e6 / count


def context_lifetime():
    references = []
    for _ in range(30):
        session = Session()
        session.contexts.add("candidate", Document())
        session.contexts.select("candidate")
        session.command("preferences.get")
        session.contexts.select("")
        references.append(weakref.ref(session))
        session.close()
    del session
    gc.collect()
    assert all(reference() is None for reference in references)
    return len(references)


def run():
    session = Session()
    try:
        dispatch(session, 100)
        measurements = [dispatch(session) for _ in range(7)]
    finally:
        session.close()
    assert not any(name.startswith("PySide6") for name in sys.modules)
    return dict(
        microseconds_per_command=measurements,
        median=statistics.median(measurements),
        released_sessions=context_lifetime(),
        qt_loaded=False,
    )


if __name__ == "__main__":
    Path(sys.argv[1]).write_text(json.dumps(run(), indent=2), encoding="utf-8")
