"""Frozen report jobs own their geometry; exports never alter document/save state."""

from dataclasses import asdict, dataclass
from pathlib import Path
from time import monotonic, sleep
from typing import TYPE_CHECKING, Any

from anthroforge.core.jobs import Job

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


def capture(session: "Session", selected: str, editing: bool, tissue: Any = None) -> Capture:
    from .tissue_inspection_capture import capture as tissue_view

    if selected and selected not in inspection.all_targets(session):
        raise ValueError("Unknown inspection selection.")
    view = dict(workspace=session.active_workspace, selected=selected, editing=editing)
    view.update(camera=list(session.workspace.camera), orthographic=session.workspace.orthographic)
    if tissue:
        view["tissue"] = tissue_view(session, selected, tissue)
    return Capture(
        freeze(session), view, inspection.issue_records(session), session.history.before is not None
    )


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
) -> dict[str, Any]:
    target = Path(path).resolve()
    validate(session, target)
    frozen = capture(session, selected, editing, tissue)
    return submit_export(session, target, frozen, wait)


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
        workload=lambda _: task_workloads.project_save(
            frozen.source.resources, frozen.source.document
        ),
    )
