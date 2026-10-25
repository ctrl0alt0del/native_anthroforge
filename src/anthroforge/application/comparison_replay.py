"""Explicit replay in an isolated session; archive content cannot dispatch arbitrary commands."""

import hashlib
import json
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from time import monotonic, sleep
from typing import Any

from anthroforge import __version__

from . import comparison_geometry, inspection, projects, report_archive, storage
from .comparison_journal import BOUNDARIES, SUPPORTED
from .inspection_context import freeze
from .preferences import PreferenceStore

MEMBERS = frozenset(
    (
        "manifest.json",
        "inspection.json",
        "image.png",
        "before.png",
        "replay.json",
        "starting.anthroforge",
    )
)


def replay(path: str, output: str = "") -> dict[str, Any]:
    from threading import Event

    with tempfile.TemporaryDirectory(prefix="anthroforge-replay-") as directory:
        root = Path(directory)
        journal = unpack(Path(path), root, Event())
        return execute(root, journal, output)


def unpack(path: Path, root: Path, cancel: Any) -> dict[str, Any]:
    with zipfile.ZipFile(path) as archive:
        validate_members(archive)
        manifest = json.loads(archive.read("manifest.json"))
        validate_manifest(manifest, archive.namelist())
        for name, checksum in manifest["checksums"].items():
            copy_checked(archive, name, root / name, checksum, cancel)
    journal = json.loads((root / "replay.json").read_text("utf-8"))
    validate_journal(journal)
    validate_project(root / "starting.anthroforge")
    return dict(journal)


def validate_project(path: Path) -> None:
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        if sum(info.file_size for info in infos) > 8 * 1024**3:
            raise ValueError("Replay project exceeds its expanded storage budget.")
        if len(infos) > 100000 or len({i.filename for i in infos}) != len(infos):
            raise ValueError("Replay project has duplicate or excessive members.")
        for info in infos:
            if unsafe_name(info.filename):
                raise ValueError("Unsafe replay project member name.")
        if archive.getinfo("manifest.json").file_size > 64 * 1024**2:
            raise ValueError("Replay project manifest exceeds its storage budget.")


def unsafe_name(value: str) -> bool:
    name = PurePosixPath(value)
    return name.is_absolute() or ".." in name.parts or "\\" in value or ":" in value


def validate_members(archive: Any) -> None:
    names = archive.namelist()
    if len(names) != len(set(names)) or set(names) - MEMBERS:
        raise ValueError("Unexpected or duplicate comparison archive member.")
    if not {"manifest.json", "replay.json", "starting.anthroforge"} <= set(names):
        raise ValueError("This report does not contain replay evidence.")
    for info in archive.infolist():
        limit = 8 * 1024**3 if info.filename == "starting.anthroforge" else 64 * 1024**2
        if info.file_size > limit or info.flag_bits & 1:
            raise ValueError("Replay member exceeds its size limit or is encrypted.")


def validate_manifest(manifest: Any, names: Any) -> None:
    if manifest.get("format") != "anthroforge-comparison" or manifest.get("version") != 1:
        raise ValueError("Unsupported comparison archive format.")
    if manifest.get("application_version") != __version__:
        raise ValueError("Replay requires the same application version as the report.")
    if set(manifest.get("checksums", {})) != set(names) - {"manifest.json"}:
        raise ValueError("Every replay archive member requires a checksum.")


def copy_checked(archive: Any, name: str, path: Path, checksum: str, cancel: Any) -> None:
    digest = hashlib.sha256()
    with archive.open(name) as source, path.open("wb") as output:
        while block := source.read(1024 * 1024):
            report_archive.check(cancel)
            digest.update(block)
            output.write(block)
    if digest.hexdigest() != checksum:
        raise ValueError("Replay checksum mismatch: " + name)


def validate_journal(journal: Any) -> None:
    if journal.get("schema_version") != 1 or journal.get("application_version") != __version__:
        raise ValueError("Unsupported replay journal version.")
    if not journal.get("complete"):
        raise ValueError("Replay evidence is incomplete: " + "; ".join(journal.get("reasons", [])))
    events = journal.get("operations", [])
    if len(events) > 10000 or len(json.dumps(events).encode()) > 16 * 1024**2:
        raise ValueError("Replay journal exceeds its recording limits.")
    for event in events:
        if event.get("operation") not in SUPPORTED | BOUNDARIES:
            raise ValueError("Unsupported replay operation.")
        if not isinstance(event.get("arguments"), dict):
            raise ValueError("Replay arguments must be an object.")


def execute(root: Path, journal: Any, output: str) -> dict[str, Any]:
    from .session import Session

    session = Session(preferences=PreferenceStore())
    try:
        document, resources = storage.read_package(root / "starting.anthroforge", session.engine)
        projects.adopt(session, document, resources)
        session.preferences.update(
            routing_backend=journal["routing_backend"],
            fiber_propagation=journal.get("fiber_propagation", "LOCAL_SURFACE"),
        )
        return replay_result(session, journal, output)
    finally:
        session.close()


def replay_result(session: Any, journal: Any, output: str) -> dict[str, Any]:
    before = freeze(session)
    run_events(session, journal["operations"])
    result = comparison_geometry.compare(before, freeze(session))
    if output:
        projects.save(session, output, "wait")
    return dict(
        comparison=result,
        issues=inspection.issue_records(session),
        timing="Semantic order only; dispatch timing is not deterministic",
    )


def run_events(session: Any, events: Any) -> None:
    for event in events:
        if event["operation"] == "wait":
            settle(session)
        else:
            session.command(event["operation"], **event["arguments"])
        session.scheduler.tick()
    if session.history.before is not None:
        raise ValueError("Replay ended inside a transaction.")
    settle(session)


def settle(session: Any) -> None:
    deadline = monotonic() + 180
    while session.scheduler.active_jobs:
        session.scheduler.tick()
        if monotonic() > deadline:
            raise TimeoutError("Replay calculations did not finish in time.")
        sleep(0.002)
