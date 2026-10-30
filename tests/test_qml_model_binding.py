"""Registered models are engine-local and route to the same desktop/application services."""

from contextlib import contextmanager

from PySide6.QtCore import QCoreApplication, QUrl
from PySide6.QtQml import QQmlComponent, QQmlEngine
from shiboken6 import delete

from anthroforge.desktop.controller import Controller
from anthroforge.desktop.qml_bindings import bind

PROBE = b"""import QtQml
import AnthroForge.Desktop 1.0
QtObject {
    property string name: App.project.documentName
    property string selected: App.selection.selectedId
    function createRoot(label) { return App.runtime.run("scp.empty", {name: label}); }
}"""


@contextmanager
def models():
    app = QCoreApplication.instance() or QCoreApplication([])
    controller, engine = Controller(), QQmlEngine()
    controller.timer.stop()
    bind(engine, controller)
    try:
        yield controller, engine
    finally:
        delete(engine)
        controller.close()
        assert app


def probe(engine):
    component = QQmlComponent(engine)
    component.setData(PROBE, QUrl())
    value = component.create()
    assert value, component.errors()
    return component, value


def test_two_engines_keep_separate_session_models():
    with models() as (first, a), models() as (second, b):
        component_a, view_a = probe(a)
        component_b, view_b = probe(b)
        first.session.replace_document(name="First")
        first.refresh()
        assert view_a.property("name") == "First"
        assert view_b.property("name") == "Untitled"
        target = first.run("scp.empty", dict(name="Bone"))
        assert view_a.property("selected") == target
        assert view_b.property("selected") == ""
        assert not second.session.document.entities
        assert component_a and component_b


def test_model_cannot_create_an_unowned_session():
    with models() as (_, engine):
        component = QQmlComponent(engine)
        component.setData(b"import AnthroForge.Desktop 1.0\nAfSelectionView {}", QUrl())
        assert component.create() is None
        assert "belong" in "\n".join(e.toString() for e in component.errors())
