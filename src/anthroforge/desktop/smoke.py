import json
from pathlib import Path
from time import monotonic

from PySide6.QtCore import QTimer


def save_frame(frame, screenshot: str | None) -> bool:
    if screenshot:
        target = Path(screenshot).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        return frame.save(str(target))
    return True


def finish(app, engine, screenshot: str | None, warnings: list[str], controller=None) -> None:
    frame = engine.rootObjects()[0].grabWindow()
    saved = save_frame(frame, screenshot) if not frame.isNull() else False
    valid = not frame.isNull() and not warnings and saved
    report = summary(frame, screenshot, warnings, valid, controller)
    print(json.dumps(report))
    app.exit(0 if valid else 1)


def summary(frame, screenshot, warnings, valid, controller):
    return dict(
        desktop_smoke=valid,
        warnings=warnings,
        frame=[frame.width(), frame.height()],
        screenshot=screenshot,
        entities=len(controller.session.document.entities) if controller else None,
        projects=project_status(controller) if controller else None,
        preferences=getattr(controller, "smoke_preferences", None),
    )


def schedule(
    app, engine, screenshot: str | None, warnings: list[str], panel="", controller=None
) -> None:
    if panel:
        QTimer.singleShot(500, lambda: show_panel(engine.rootObjects()[0], controller, panel))
    deadline = monotonic() + 60
    QTimer.singleShot(
        2000, lambda: settled(app, engine, screenshot, warnings, controller, deadline)
    )


def ready(controller) -> bool:
    return controller is None or (
        controller.pending_document is None
        and not controller.session.waiting_save
        and not controller.session.scheduler.active_jobs
        and not any(model.pending for model in controller.geometry_models())
    )


def settled(app, engine, screenshot, warnings, controller, deadline) -> None:
    if not ready(controller) and monotonic() < deadline:
        QTimer.singleShot(
            50, lambda: settled(app, engine, screenshot, warnings, controller, deadline)
        )
        return
    if not ready(controller):
        warnings.append(
            "Desktop smoke timed out waiting for project/evaluation/viewport readiness."
        )
    if controller is not None:
        warnings.extend(controller.session.scheduler.errors)
    finish(app, engine, screenshot, warnings, controller)


def show_panel(window, controller, panel):
    if panel == "recovery":
        from .smoke_projects import start

        start(controller)
        return
    if panel == "preferences":
        from .smoke_preferences import show

        show(window, controller)
        return
    window.setProperty(panel + "Open", True)
    if panel == "issues" and controller.issue_panel.model.rows:
        controller.issue_panel.selectIssue(controller.issue_panel.model.rows[0]["issueId"])


def project_status(controller):
    library = controller.project_library
    return dict(
        recent=library.recent.entries,
        recovery=library.autosave.last,
        copies=len(library.recovery_browser.rows),
        path=str(controller.session.path or ""),
        dirty=controller.session.document.revision != controller.session.saved_revision,
    )
