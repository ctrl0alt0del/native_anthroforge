"""Frozen comparison reports with streamed assets and independently verifiable checksums."""

import hashlib
import json
import os
import tempfile
import zipfile
from dataclasses import replace
from pathlib import Path
from typing import Any

from anthroforge import __version__
from anthroforge.profiling.identity import build_identity

from . import comparison_geometry, inspection_report, report_archive
from .report_renderer import render
from .storage import write_package


def write(path: Path, frozen: Any, metadata: Any, cancel: Any) -> str:
    with tempfile.TemporaryDirectory(prefix="anthroforge-comparison-") as directory:
        root = Path(directory)
        current = render_capture(root / "after", frozen, cancel)
        before = baseline_capture(frozen)
        previous = render_capture(root / "before", before, cancel)
        files = dict(image=current, before=previous)
        data = evidence(frozen, cancel)
        metadata.update(application_version=__version__, comparison=data)
        package(path, root, frozen, files, metadata, cancel)
    return str(path)


def render_capture(root: Path, frozen: Any, cancel: Any) -> Path:
    root.mkdir()
    report_archive.check(cancel)
    write_package(root / "snapshot.anthroforge", frozen.source.document, frozen.source.resources)
    (root / "view.json").write_text(json.dumps(frozen.view), encoding="utf-8")
    render(root, frozen.source.document.revision, cancel)
    image = json.loads((root / "image.png.json").read_text(encoding="utf-8"))
    report_archive.verify(image, inspection_report.metadata(frozen))
    return root / "image.png"


def baseline_capture(frozen: Any) -> Any:
    baseline = frozen.comparison.baseline
    source = baseline.source
    document = replace(source.document, workspaces=frozen.source.document.workspaces)
    source = replace(source, document=document, workspace=frozen.source.workspace)
    view = dict(frozen.view, editing=False)
    view.pop("tissue", None)
    view.pop("route", None)
    if view["selected"] not in source.document.registry.records:
        view["selected"] = ""
    return inspection_report.Capture(source, view, {}, baseline.provisional)


def evidence(frozen: Any, cancel: Any) -> dict[str, Any]:
    value = frozen.comparison
    report_archive.check(cancel)
    data = comparison_metadata(frozen)
    data["differences"] = comparison_geometry.compare(
        value.baseline.source, frozen.source, getattr(cancel, "handle", 0)
    )
    return data


def comparison_metadata(frozen: Any) -> dict[str, Any]:
    value = frozen.comparison
    return dict(
        baseline_id=value.baseline.id,
        build=build_identity(),
        before=value.baseline.evidence,
        after=value.evidence,
        before_provisional=value.baseline.provisional,
        after_provisional=frozen.provisional,
        issues=value.issues,
        before_issues=value.baseline.issues,
        replay=value.journal if value.replay else dict(included=False),
    )


def package(path: Path, root: Path, frozen: Any, images: Any, data: Any, cancel: Any) -> None:
    files = {"image.png": images["image"], "before.png": images["before"]}
    (root / "inspection.json").write_text(json.dumps(data, indent=2, allow_nan=False), "utf-8")
    files["inspection.json"] = root / "inspection.json"
    if frozen.comparison.replay:
        files.update(replay_files(root, frozen))
    manifest = dict(format="anthroforge-comparison", version=1, application_version=__version__)
    manifest["checksums"] = {key: digest(value, cancel) for key, value in files.items()}
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2), "utf-8")
    files["manifest.json"] = root / "manifest.json"
    archive(path, files, cancel)


def replay_files(root: Path, frozen: Any) -> dict[str, Path]:
    value = frozen.comparison
    source = value.baseline.source
    write_package(root / "starting.anthroforge", source.document, source.resources)
    journal = dict(
        value.journal,
        routing_backend=source.routing_backend,
        application_version=__version__,
        schema_version=1,
    )
    (root / "replay.json").write_text(json.dumps(journal, allow_nan=False), "utf-8")
    return {name: root / name for name in ("starting.anthroforge", "replay.json")}


def digest(path: Path, cancel: Any) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(1024 * 1024):
            report_archive.check(cancel)
            value.update(block)
    return value.hexdigest()


def archive(path: Path, files: Any, cancel: Any) -> None:
    descriptor, name = tempfile.mkstemp(prefix=".afinspection-", dir=path.parent)
    os.close(descriptor)
    try:
        with zipfile.ZipFile(name, "w", compression=zipfile.ZIP_DEFLATED) as target:
            for member, source in files.items():
                stream_file(target, member, source, cancel)
        report_archive.check(cancel)
        with open(name, "r+b") as stream:
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def stream_file(target: Any, member: str, path: Path, cancel: Any) -> None:
    with target.open(member, "w", force_zip64=True) as output, path.open("rb") as source:
        while block := source.read(1024 * 1024):
            report_archive.check(cancel)
            output.write(block)
