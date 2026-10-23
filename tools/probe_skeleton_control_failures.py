"""Distinguish migrated-control failures from the same edit in the immutable assembly."""

import json
import sys
from contextlib import closing
from pathlib import Path

from skeleton_shortcut_exercise import changed_value

from anthroforge.application.projects import adopt, synchronize_loaded
from anthroforge.application.session import Session
from anthroforge.application.storage import read_package


def failures(session):
    return [
        dict(label=j.label, outputs=sorted(j.outputs), error=j.error)
        for j in session.scheduler.jobs
        if j.state == "failed"
    ]


def check(path, mapping):
    with closing(Session()) as session:
        adopt(session, *read_package(path, session.engine))
        synchronize_loaded(session)
        session.wait(120)
        value = changed_value(mapping["value"])
        session.command("property.set", reference=mapping["reference"], value=value)
        session.wait(120)
        return failures(session)


def run(folder, number):
    mappings = json.loads((folder / "compact-mapping.json").read_text())
    mapping = mappings["SHORTCUT_" + number]
    result = {
        name: check(folder / name, mapping)
        for name in ("input.anthroforge", "compact-checkpoint.anthroforge")
    }
    (folder / ("failure-" + number + ".json")).write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    run(Path(sys.argv[1]), sys.argv[2])
