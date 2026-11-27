"""Exercise native-window anatomy expansion, nested collapse, search and selection."""

import json
from pathlib import Path

from PySide6.QtCore import QPointF
from PySide6.QtTest import QTest
from shiboken6 import delete
from ui_acceptance import click, find

from anthroforge.core.entities import SCP
from anthroforge.desktop.app import create_engine
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.qt_profiler import profiler_application
from anthroforge.desktop.runtime import native_runtime
from anthroforge.desktop.style import configure

OUTPUT = Path("build/anatomy-tree-review").resolve()
ORDER = ["root", "arm", "upper", "hand", "lower", "leg", "foot"]


def entities():
    links = [
        ("root", ""),
        ("arm", "root"),
        ("leg", "root"),
        ("upper", "arm"),
        ("foot", "leg"),
        ("lower", "arm"),
        ("hand", "upper"),
    ]
    return tuple(SCP(key.title(), id=key, parent=parent) for key, parent in links)


def setup(controller):
    controller.session.replace_document(entities=entities())
    controller.refresh()
    controller.selection_view.select("upper")
    controller.session.command("save", path=str(OUTPUT / "tree.anthroforge"), blocked_policy="wait")
    controller.session.wait()


def visible(window):
    rows = find(window, "hierarchy").property("model")
    if hasattr(rows, "toVariant"):
        rows = rows.toVariant()
    return [row["id"] for row in rows]


def toggle(window, key):
    name = "expand_" + key
    button = find(window, name)
    point = button.mapToScene(QPointF(button.width() / 2, button.height() / 2))
    QTest.mouseMove(window, point.toPoint())
    QTest.qWait(100)
    click(window, name)


def expanded(window):
    assert visible(window) == ORDER
    toggle(window, "arm")
    assert window.grabWindow().save(str(OUTPUT / "collapsed.png"))
    assert visible(window) == ["root", "arm", "leg", "foot"], visible(window)
    toggle(window, "leg")
    assert visible(window) == ["root", "arm", "leg"]
    toggle(window, "arm")
    assert visible(window) == ORDER[:-1]
    toggle(window, "leg")
    assert visible(window) == ORDER


def nested(window):
    toggle(window, "upper")
    toggle(window, "arm")
    toggle(window, "arm")
    assert visible(window) == [key for key in ORDER if key != "hand"]
    toggle(window, "upper")
    assert visible(window) == ORDER


def search(window):
    toggle(window, "arm")
    field = find(window, "outlinerSearch")
    field.setProperty("text", "hand")
    QTest.qWait(80)
    assert visible(window) == ["hand"]
    field.setProperty("text", "")
    QTest.qWait(80)
    assert visible(window) == ["root", "arm", "leg", "foot"]
    toggle(window, "arm")
    assert visible(window) == ORDER


def inspect(controller, window, warnings):
    window.resize(1280, 900)
    QTest.qWait(700)
    expanded(window)
    nested(window)
    search(window)
    assert controller.selection == "upper"
    assert window.grabWindow().save(str(OUTPUT / "expanded.png"))
    assert not warnings, warnings
    report = dict(passed=True, order=visible(window), collapse=True, search=True, selection=True)
    (OUTPUT / "acceptance.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report))


def run():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    configure()
    app = profiler_application()
    with native_runtime():
        controller, warnings = Controller(), []
        setup(controller)
        engine = create_engine(controller, warnings)
        try:
            inspect(controller, engine.rootObjects()[0], warnings)
        finally:
            controller.close()
            delete(engine)
    assert app


if __name__ == "__main__":
    run()
