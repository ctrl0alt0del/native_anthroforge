"""Snapshot exports use the existing scheduler and optional isolated desktop renderer."""

import json
import os
import tempfile
import zipfile
from pathlib import Path
from typing import Any

from anthroforge.core.jobs import Job
from anthroforge.core.scheduling import Workload
from anthroforge.native.mesh import NativeCancellation

from . import (
    inspection_report,
    inspection_scene_bundle,
    inspection_snapshots,
    report_archive,
    report_renderer,
)


def export(
    session: Any,
    path: str,
    snapshot: str,
    images: bool = True,
    view: Any = None,
    wait: bool = False,
) -> dict[str, Any]:
    target = inspection_report.export_target(session, path)
    frozen = inspection_snapshots.selected(session, snapshot)
    job = make_job(target, frozen, images, view_settings(frozen, view))
    session.scheduler.submit(job)
    if wait:
        inspection_report.wait_for_export(session, job)
    return dict(job=job.id, snapshot=snapshot, path=str(target), state=job.state)


def view_settings(snapshot: Any, options: Any) -> dict[str, Any]:
    view = dict(mode="Split", camera=list(snapshot.camera), hidden=[], mirrors="Both")
    view.update(options or {})
    if view["mode"] not in ("Before", "After", "Split", "Overlay"):
        raise ValueError("Choose Before, After, Split or Overlay.")
    if view["mirrors"] not in ("Both", "Source only", "Mirror only"):
        raise ValueError("Unknown mirror presentation.")
    if len(view["camera"]) != 7 or not all(finite_number(v) for v in view["camera"]):
        raise ValueError("An inspection camera needs seven finite values.")
    return dict(json.loads(json.dumps(view, allow_nan=False)))


def finite_number(value: Any) -> bool:
    from math import isfinite

    return isinstance(value, (int, float)) and isfinite(value)


def make_job(target: Path, snapshot: Any, images: bool, view: Any) -> Job:
    return Job(
        "Export candidate inspection",
        frozenset(("@file:" + str(target),)),
        lambda _: snapshot,
        lambda frozen, cancel: write(target, frozen, images, view, cancel),
        lambda _: None,
        writes=False,
        publish_during_edit=True,
        kind="inspection_report",
        cancel=NativeCancellation(snapshot.engine),
        workload=lambda _: Workload(),
    )


def write(target: Path, snapshot: Any, images: bool, view: Any, cancel: Any) -> str:
    with tempfile.TemporaryDirectory(prefix="anthroforge-inspection-") as directory:
        root = Path(directory)
        inspection_scene_bundle.write(root, snapshot, view, cancel)
        if images:
            report_renderer.render_scene(root, cancel)
            verify_image(root, snapshot, view)
        archive(target, root, cancel)
    return str(target)


def verify_image(root: Path, snapshot: Any, view: Any) -> None:
    evidence = json.loads((root / "image.png.json").read_text(encoding="utf-8"))
    if not evidence.get("captured") or evidence.get("snapshot") != snapshot.identity:
        raise ValueError("Renderer did not capture the requested inspection snapshot.")
    if evidence.get("view") != view or not (root / "image.png").is_file():
        raise ValueError("Renderer did not preserve the requested inspection view.")


def archive(target: Path, root: Path, cancel: Any) -> None:
    descriptor, temporary = tempfile.mkstemp(prefix=".afinspection-", dir=target.parent)
    os.close(descriptor)
    try:
        write_archive(Path(temporary), root, cancel)
        report_archive.check(cancel)
        with open(temporary, "r+b") as stream:
            os.fsync(stream.fileno())
        os.replace(temporary, target)
    finally:
        Path(temporary).unlink(missing_ok=True)


def write_archive(target: Path, root: Path, cancel: Any) -> None:
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        files = sorted(root.rglob("*.npy")) + [root / "inspection.json"]
        files.extend(
            path for path in (root / "image.png", root / "image.png.json") if path.exists()
        )
        for path in files:
            report_archive.check(cancel)
            archive.write(path, path.relative_to(root).as_posix())
