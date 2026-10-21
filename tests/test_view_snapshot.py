"""Large QML overlays cross the Python boundary once per change, not once per point."""

from pathlib import Path

from PySide6.QtCore import QCoreApplication, QObject, QUrl, Signal, Slot
from PySide6.QtQml import QQmlComponent, QQmlEngine

QML = b"""import QtQuick
ViewSnapshot {
    source: witness
    property real total: {
        const points=data.lines || [];
        let result=0;
        for (let i=0; i<points.length; ++i) result += points[i][0];
        return result;
    }
}"""


class Witness(QObject):
    changed = Signal()

    def __init__(self):
        super().__init__()
        self.calls, self.offset = 0, 1

    @Slot(result="QVariantMap")
    def snapshot(self):
        self.calls += 1
        return dict(lines=[[self.offset, 0, 0]] * 8192)


def observer(source):
    engine = QQmlEngine()
    engine.rootContext().setContextProperty("witness", source)
    component = QQmlComponent(engine)
    base = Path("src/anthroforge/desktop/qml/SnapshotTest.qml").resolve()
    component.setData(QML, QUrl.fromLocalFile(str(base)))
    value = component.create()
    assert value, component.errors()
    return engine, component, value


def test_large_snapshot_is_copied_once_per_update():
    app = QCoreApplication.instance() or QCoreApplication([])
    source = Witness()
    engine, component, value = observer(source)
    count = source.calls
    assert value.property("total") == 8192 and count <= 2
    for _ in range(100):
        assert value.property("total") == 8192
    assert source.calls == count
    source.offset = 2
    source.changed.emit()
    assert value.property("total") == 16384 and source.calls == count + 1
    assert app and engine and component
    value.deleteLater()
