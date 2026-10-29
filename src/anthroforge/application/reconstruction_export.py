"""Inspection archives freeze both stage selections, provenance, metrics and camera."""

from dataclasses import replace
from pathlib import Path
from typing import Any

from . import inspection_report, reconstruction_views
from .inspection_context import InspectionContext


def export(
    session: Any, path: str, camera: Any = None, mode: str = "Split", wait: bool = False
) -> Any:
    service = session.reconstruction_comparison
    if not service.value or service.value.state != "ready":
        raise ValueError("Wait for a completed reconstruction comparison before exporting.")
    inspection_report.export_target(session, path)
    frozen = capture(service, camera, mode)
    return inspection_report.submit_export(session, Path(path).resolve(), frozen, wait)


def capture(service: Any, camera: Any, mode: str) -> Any:
    if mode not in ("Split", "Before", "After", "Overlay"):
        raise ValueError("Choose a supported comparison layout.")
    document, resources = service.project, service.resources
    workspace = replace(
        document.workspaces[0], camera=tuple(camera or document.workspaces[0].camera)
    )
    source = InspectionContext(document, resources, service.session.engine, workspace)
    return inspection_report.Capture(source, presentation(service, workspace, mode), {}, False)


def presentation(service: Any, workspace: Any, mode: str) -> Any:
    comparison = dict(
        mode=mode,
        report=service.value.asset,
        selections=[reconstruction_views.report(v) for v in service.pair],
    )
    return dict(
        workspace=0,
        selected="",
        editing=False,
        camera=list(workspace.camera),
        orthographic=False,
        reconstruction=comparison,
    )
