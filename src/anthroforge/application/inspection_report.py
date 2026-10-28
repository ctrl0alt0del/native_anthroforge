"""Frozen report jobs own their geometry; exports never alter document/save state."""

import json
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from time import monotonic, sleep
from typing import TYPE_CHECKING, Any

from anthroforge.core.jobs import Job
from anthroforge.native.mesh import NativeCancellation

from . import inspection, measurements, report_archive, task_workloads
from .inspection_context import InspectionContext, freeze

if TYPE_CHECKING:
    from .session import Session


@dataclass(frozen=True)
class Capture:
    source: InspectionContext
    view: dict[str, Any]
    issues: dict[str, Any]
    provisional: bool
    comparison: Any = None


def capture(
    session: "Session", selected: str, editing: bool, tissue: Any = None, route: Any = None
) -> Capture:
    if selected and selected not in inspection.all_targets(session):
        raise ValueError("Unknown inspection selection.")
    view = dict(workspace=session.active_workspace, selected=selected, editing=editing)
    view.update(camera=list(session.workspace.camera), orthographic=session.workspace.orthographic)
    capture_views(session, view, tissue, route)
    view = json.loads(json.dumps(view, allow_nan=False))
    return Capture(
        freeze(session), view, inspection.issue_records(session), session.history.before is not None
    )


def capture_views(session: Any, view: Any, tissue: Any, route: Any) -> None:
    from .route_inspection import capture as route_view
    from .tissue_inspection_capture import capture as tissue_view

    if tissue:
        view["tissue"] = tissue_view(session, view["selected"], tissue)
    if route:
        view["route"] = route_view(session, view["selected"], route)


def metadata(frozen: Capture) -> dict[str, Any]:
    source = frozen.source
    return dict(
        schema_version=1,
        format="anthroforge-inspection",
        document=str(source.document.id),
        revision=source.document.revision,
        provisional=frozen.provisional,
        view=frozen.view,
        coordinate_system="right-handed Z-up; canonical metres; row-major affine matrices",
        workspace=asdict(source.workspace),
        measurements=measurements.inspect(source),
        issues=frozen.issues,
        entities=[inspection.target(source, key) for key in inspection.all_targets(source)],
    )


def export(
    session: "Session",
    path: str,
    selected: str = "",
    editing: bool = False,
    wait: bool = False,
    tissue: Any = None,
    route: Any = None,
    comparison: bool = True,
    replay: bool = False,
    spatial: Any = None,
) -> dict[str, Any]:
    frozen = export_capture(session, path, selected, editing, tissue, route, spatial)
    frozen = comparison_options(session, frozen, comparison, replay)
    return submit_export(session, Path(path).resolve(), frozen, wait)


def export_capture(
    session: Any, path: str, selected: str, editing: bool, tissue: Any, route: Any, spatial: Any
) -> Capture:
    export_target(session, path)
    frozen = capture(session, selected, editing, tissue, route)
    from .inspection_spatial_capture import capture as capture_spatial

    capture_spatial(session, frozen, spatial or {})
    return frozen


def capture_finding(session: Any, frozen: Capture, finding: Any) -> None:
    from .spatial_evidence import capture as finding_view

    if finding:
        frozen.view["finding"] = json.loads(json.dumps(finding_view(session, finding)))


def export_target(session: Any, path: str) -> Path:
    target = Path(path).resolve()
    validate(session, target)
    return target


def comparison_options(session: Any, frozen: Capture, comparison: bool, replay: bool) -> Capture:
    from .comparison_capture import capture as capture_comparison

    if replay and not comparison:
        raise ValueError("Replay requires comparison evidence.")
    return replace(frozen, comparison=capture_comparison(session, replay)) if comparison else frozen


def submit_export(session: "Session", target: Path, frozen: Capture, wait: bool) -> dict[str, Any]:
    job = create_job(target, frozen)
    session.scheduler.submit(job)
    if wait:
        wait_for_export(session, job)
    return dict(
        job=job.id, path=str(target), revision=frozen.source.document.revision, state=job.state
    )


def wait_for_export(session: "Session", job: Job) -> None:
    deadline = monotonic() + 180
    while job.active and monotonic() < deadline:
        session.scheduler.tick()
        sleep(0.005)
    if job.active:
        session.scheduler.cancel_job(job.id)
    if job.state != "succeeded":
        raise ValueError(job.error or "Inspection export " + job.state)


def validate(session: "Session", target: Path) -> None:
    if not target.name.endswith(".afinspection.zip"):
        raise ValueError("Inspection reports require an .afinspection.zip filename.")
    if any(j.active and j.kind == "inspection_report" for j in session.scheduler.jobs):
        raise ValueError("An inspection report is already being exported.")


def create_job(path: Path, frozen: Capture) -> Job:
    return Job(
        "Export inspection report",
        frozenset(("@file:" + str(path),)),
        lambda _: frozen,
        lambda snapshot, cancel: report_archive.write(path, snapshot, metadata(snapshot), cancel),
        lambda _: None,
        writes=False,
        publish_during_edit=True,
        kind="inspection_report",
        cancel=NativeCancellation(frozen.source.engine),
        workload=lambda _: task_workloads.project_save(
            frozen.source.resources, frozen.source.document
        ),
    )
