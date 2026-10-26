"""Measure production-resolution envelope behavior independently of low-resolution tests."""

import json
import os
import sys
from pathlib import Path
from time import perf_counter

from anthroforge.application.session import Session


def build(session, output):
    key = session.command(
        "import", path=str(Path("examples/primitives/cube.obj").resolve()), units=1
    )
    session.wait()
    session.command("workspace.update", hidden=[key["entity_id"]])
    session.command("profile.start")
    started = perf_counter()
    job = session.command("skin.envelope.build")
    session.wait()
    report(session, job, started, output)
    session.command("profile.stop", path=str(output / "DEFAULT.afprofile.zip"), wait=True)
    session.command("save", path=str(output / "DEFAULT.anthroforge"), blocked_policy="wait")
    session.wait()


def report(session, job, started, output):
    state = session.scheduler.registry.by_id[job]
    assert state.state == "succeeded", state.error
    stage = session.document.skin.envelope
    mesh = session.assets[stage.asset].mesh
    metadata = json.loads(session.resources.skin[stage.data].metadata)
    result = dict(
        seconds=perf_counter() - started, counts=mesh.counts, bounds=mesh.bounds, **metadata
    )
    (output / "production-envelope.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result))


def main():
    output = Path(sys.argv[1]).resolve()
    output.mkdir(parents=True, exist_ok=True)
    os.environ["ANTHROFORGE_PREFERENCES_PATH"] = str(output / "preferences.json")
    session = Session("Production envelope qualification")
    try:
        build(session, output)
    finally:
        session.close()


if __name__ == "__main__":
    main()
