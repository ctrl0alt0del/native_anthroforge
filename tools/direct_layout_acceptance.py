"""Check reported button truncation/centering and actual tabs at caller-selected DPI."""

import json
import os
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtCore import QPointF
from PySide6.QtGui import QFont, QFontDatabase
from tissue_editor_acceptance import (
    QQuickStyle,
    delete,
    native_runtime,
    profiler_application,
    run,
    settle,
)
from ui_polish_acceptance import descendants

OUTPUT = Path("build/ui-direct-workflows")


def buttons(window):
    return [
        item
        for item in descendants(window.contentItem())
        if item.isVisible() and item.metaObject().indexOfProperty("glyph") >= 0
    ]


def content(button):
    return [
        item
        for item in descendants(button.property("contentItem"))
        if item.isVisible() and item.metaObject().indexOfProperty("truncated") >= 0
    ]


def check_label(button):
    rows = content(button)
    assert not any(row.property("truncated") for row in rows), button.property("text")
    for row in rows:
        center = row.mapToItem(button, QPointF(row.width() / 2, row.height() / 2))
        assert abs(center.y() - button.height() / 2) <= 1, button.property("text")


def inspect(controller, window):
    scale = os.environ.get("QT_SCALE_FACTOR", "1")
    width = int(os.environ.get("AF_LAYOUT_WIDTH", "1920" if scale == "2" else "1440"))
    window.resize(width, 1027 if scale == "2" else 900)
    controller.selection_view.select(controller.run("scp.empty", dict(name="Selected anatomy")))
    settle(controller)
    labels = {"Save", "Manage…", "Focus", "Recalculate", "Ruler", "Create Tissue"}
    checked = [b for b in buttons(window) if b.property("text") in labels]
    assert {b.property("text") for b in checked} == labels
    for button in checked:
        check_label(button)
    record(window, checked, scale, width)
    check_tabs(window)
    check_icons(window)


def record(window, checked, scale, width):
    output = [dict(text=b.property("text"), width=b.width()) for b in checked]
    (OUTPUT / f"layout-{scale}-{width}.json").write_text(json.dumps(output), encoding="utf-8")
    assert window.grabWindow().save(str(OUTPUT / f"layout-{scale}-{width}.png"))


def check_icons(window):
    for button in buttons(window):
        if not button.property("glyph") or button.property("text"):
            continue
        icon = next(i for i in descendants(button.property("contentItem")) if i.property("source"))
        center = icon.mapToItem(button, QPointF(icon.width() / 2, icon.height() / 2))
        assert abs(center.x() - button.width() / 2) <= 1, button.objectName()
        assert abs(center.y() - button.height() / 2) <= 1, button.objectName()


def check_tabs(window):
    items = descendants(window.contentItem())
    for name in ("anatomyTab", "constructionTab"):
        tab = next(item for item in items if item.objectName() == name)
        assert "TabButton" in tab.metaObject().className()


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
        app.setFont(QFont("Segoe UI"))
        try:
            run(inspect)
            print("Report layout checks passed.", flush=True)
        finally:
            delete(app)


if __name__ == "__main__":
    main()
