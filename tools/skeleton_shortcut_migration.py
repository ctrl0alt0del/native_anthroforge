"""Explicit one-file data migration; no source mutation or geometry fallback."""

import hashlib
import json
import shutil
import sys
from contextlib import closing
from pathlib import Path

from anthroforge.application.session import Session
from anthroforge.application.storage import document_state

SOCKETS = {
    "Socket_12": (0, "length"),
    "Socket_2": (1, "length"),
    "Socket_3": (2, "length"),
    "Socket_4": (3, "length"),
    "Socket_13": (0, "radius"),
    "Socket_8": (1, "radius"),
    "Socket_9": (2, "radius"),
    "Socket_10": (3, "radius"),
}


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def digit_reference(session, shortcut):
    owner = session.document.entity(shortcut["owner_id"])
    if owner.primitive is None or owner.primitive.kind != "SEGMENT_CHAIN":
        return None
    socket = shortcut["resolved"]["path"].split('"')[-2]
    index, field = SOCKETS[socket]
    return dict(target=owner.id, path=["primitive", "chain", "segments", f"#{index}", field])


def expose_digit(session, shortcut):
    reference = digit_reference(session, shortcut)
    if reference is None:
        return None
    current = session.command("property.get", reference=reference)["value"]
    original = shortcut["resolved"]["captured"]["value"]
    if abs(current - original) > 1e-12:
        raise ValueError(f"Source/destination digit value differs: {shortcut['name']}")
    identity = session.command("shortcut.expose", reference=reference, label=shortcut["name"])
    return dict(source=shortcut["id"], wrapper=identity, reference=reference, value=current)


def unchanged(before, after):
    excluded = {"revision", "shortcuts", "shortcut_order"}
    for key, value in before.items():
        if key not in excluded and value != after[key]:
            raise AssertionError("Shortcut exposure changed existing document field: " + key)


def digit_stage(session, definitions, output):
    before = document_state(session.document)
    session.begin()
    mappings = [expose_digit(session, s) for s in definitions["roots"]["AF_ROOT"]["shortcuts"]]
    session.commit()
    session.wait(120)
    mappings = [m for m in mappings if m is not None]
    assert len(mappings) == 80
    unchanged(before, document_state(session.document))
    session.command(
        "save", path=str(output / "digits-checkpoint.anthroforge"), blocked_policy="wait"
    )
    return mappings


def run(source, definitions_path, output):
    output.mkdir(parents=True, exist_ok=True)
    baseline = output / "input.anthroforge"
    if baseline.exists():
        assert digest(baseline) == digest(source), "Existing recovery input differs."
    else:
        shutil.copyfile(source, baseline)
    definitions = json.loads(definitions_path.read_text(encoding="utf-8"))
    with closing(Session()) as session:
        session.command("open", path=str(baseline))
        session.wait(120)
        mappings = digit_stage(session, definitions, output)
    result = dict(input_sha256=digest(source), mappings=mappings, status="digits only; incomplete")
    (output / "migration.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Exposed {len(mappings)} digit controls; all existing document records unchanged.")


if __name__ == "__main__":
    run(*(Path(value) for value in sys.argv[1:4]))
