import json
from pathlib import Path

from PySide6.QtCore import QMetaObject, QObject, QTimer


def save_frame(frame, screenshot: str | None) -> bool:
    if screenshot:
        target = Path(screenshot).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        return frame.save(str(target))
    return True


def finish(app, engine, screenshot: str | None, warnings: list[str]) -> None:
    frame = engine.rootObjects()[0].grabWindow()
    saved = save_frame(frame, screenshot) if not frame.isNull() else False
    valid = not frame.isNull() and not warnings and saved
    print(
        json.dumps(
            {
                "desktop_smoke": valid,
                "warnings": warnings,
                "frame": [frame.width(), frame.height()],
                "screenshot": screenshot,
            }
        )
    )
    app.exit(0 if valid else 1)


def schedule(
    app, engine, screenshot: str | None, warnings: list[str], panel="", controller=None
) -> None:
    if panel:
        QTimer.singleShot(500, lambda: show_panel(engine.rootObjects()[0], controller, panel))
    QTimer.singleShot(2000, lambda: finish(app, engine, screenshot, warnings))


def show_panel(window, controller, panel):
    if panel == "preferences":
        dialog = window.findChild(QObject, "preferencesDialog")
        assert dialog is not None and QMetaObject.invokeMethod(dialog, "open")
        return
    window.setProperty(panel + "Open", True)
    if panel == "issues" and controller.issue_panel.model.rows:
        controller.issue_panel.selectIssue(controller.issue_panel.model.rows[0]["issueId"])
