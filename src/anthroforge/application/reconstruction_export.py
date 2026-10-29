"""Inspection archives freeze both stage selections, provenance, metrics and camera."""

import json
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
        document.workspaces[0], camera=workspace_camera(camera, document.workspaces[0].camera)
    )
    source = InspectionContext(document, resources, service.session.engine, workspace)
    view = json.loads(json.dumps(presentation(service, workspace, mode), allow_nan=False))
    return inspection_report.Capture(source, view, {}, False)


def workspace_camera(camera: Any, fallback: Any) -> tuple[float, ...]:
    values = tuple(camera) if camera is not None else (*fallback[:5], fallback[6])
    if len(values) != 6:
        raise ValueError("Comparison camera requires center XYZ, pitch, yaw and distance.")
    return (*values[:5], 0.0, values[5])


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
