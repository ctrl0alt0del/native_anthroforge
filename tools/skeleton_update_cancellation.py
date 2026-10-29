"""Full-scene cancellation responsiveness, without window creation or source mutation."""

import json
import sys
from contextlib import closing
from pathlib import Path
from time import perf_counter, sleep

from anthroforge.application.session import Session

OUTPUT = Path("build/skeleton-update-042/production/cancellation.json")


def prepare(session, path):
    session.command("skeleton_update.inspect", path=path)
    state = session.command("skeleton_update.status", wait=True)
    frames = ("SCP_8:driver-frame", "SCP_9:driver-frame", "SCP_12:driver-frame")
    return session.command(
        "skeleton_update.prepare",
        source=state["source"],
        matches={e.id: e.id for e in session.document.entities},
        mappings={k: dict(action="include") for k in frames},
    )


def cancel_running(session, state):
    job = session.scheduler.registry.by_id[state["job_id"]]
    deadline = perf_counter() + 120
    while job.state != "running" and perf_counter() < deadline:
        session.scheduler.tick()
        sleep(0.01)
    assert job.state == "running", job.state
    sleep(0.2)
    start = perf_counter()
    session.command("skeleton_update.cancel")
    request = perf_counter() - start
    session.wait(120)
    return dict(request_s=request, completed_s=perf_counter() - start, terminal=job.state)


def main():
    with closing(Session("Cancellation qualification")) as session:
        session.command("open", path=sys.argv[1])
        session.wait(600)
        original = session.document
        results = [cancel_running(session, prepare(session, sys.argv[2])) for _ in range(3)]
        assert session.document is original
        assert session.skeleton_update.runtime.preparation.candidate is None
        OUTPUT.write_text(json.dumps(results, indent=2), "utf-8")
        print(results)


if __name__ == "__main__":
    main()
