"""Update one migrated copy from fresh effective policies without changing geometry."""

import json
import sys
from contextlib import closing
from pathlib import Path

from skeleton_shortcut_pelvis import policies

from anthroforge.application.session import Session
from anthroforge.application.storage import document_state


def preserved(before, after):
    ignored = {"revision", "shortcuts", "driving_shortcuts"}
    differences = [key for key in before if key not in ignored and before[key] != after[key]]
    if differences:
        raise ValueError("Policy migration changed protected document state: " + str(differences))


def run(source, inventory, mapping, output):
    if source.resolve() == output.resolve():
        raise ValueError("Policy repair must write a new copy, preserving its source.")
    definitions, mappings = (json.loads(p.read_text()) for p in (inventory, mapping))
    with closing(Session()) as session:
        session.command("open", path=str(source))
        session.wait(600)
        before = document_state(session.document)
        session.begin()
        policies(session, mappings, definitions)
        session.commit()
        session.wait(600)
        preserved(before, document_state(session.document))
        session.command("save", path=str(output), blocked_policy="wait")


if __name__ == "__main__":
    run(*(Path(arg) for arg in sys.argv[1:5]))
