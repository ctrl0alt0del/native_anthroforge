"""Retain source polygon anchors in a migrated copy; never reinterpret face indices."""

import json
import sys
from contextlib import closing
from dataclasses import replace
from pathlib import Path

from anthroforge.application.session import Session
from anthroforge.core.attachment_provenance import receipt
from anthroforge.native.shortcut_attachments import retain_child_anchor


def corrected(session, item, source):
    runtime = source["runtime"]
    local = runtime["attach_child_origin_local"]
    record = retain_child_anchor(session.engine, item, local)
    attachment = replace(item.attachment, binding=record)
    changed = replace(item, attachment=attachment)
    return replace(changed, pose_receipt=receipt(changed, session.document.entity(item.parent)))


def run(source, capture, output, identities):
    if source.resolve() == output.resolve():
        raise ValueError("Anchor migration must preserve its source project.")
    rows = {e["id"]: e for e in json.loads(capture.read_text())["entities"]}
    with closing(Session()) as session:
        session.command("open", path=str(source))
        session.wait(600)
        session.begin()
        changes = {
            key: corrected(session, session.document.entity(key), rows[key]) for key in identities
        }
        session.replace_entities(changes)
        session.commit()
        assert not session.scheduler.errors, session.scheduler.errors
        session.command("save", path=str(output), blocked_policy="wait")


if __name__ == "__main__":
    run(*(Path(arg) for arg in sys.argv[1:4]), sys.argv[4:])
