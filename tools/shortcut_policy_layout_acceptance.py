"""Inspect long shortcut-policy rows at the inspector's minimum width offscreen."""

import os
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtCore import QUrl
from PySide6.QtGui import QFont, QFontDatabase, QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from ui_polish_acceptance import descendants

from anthroforge.desktop import app

OUTPUT = Path("build/usability-037/policies")
QML = b"""
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
ApplicationWindow {
    visible:true; width:300; height:680; color:Theme.panel
    ShortcutPolicies {
        anchors.fill:parent; anchors.margins:12; expanded:true
        adapter:QtObject {
            property string ownerName:"Ribs"
            property var scopeOptions:[]
            property string scopeIdentity:""
            property bool preserveOwner:false
            property var descendants:[0,1,2].map(i=>({
                target:String(i),
                label:"Long anatomical descendant name requiring multiple lines "+i,
                policy:{parent_anchor:"KEEP",child_anchor:"KEEP",follow_rotation:"KEEP",strategy:"KEEP"}
            }))
        }
    }
}
"""


def inspect(engine):
    window = engine.rootObjects()[0]
    QTest.qWait(150)
    rows = [i for i in descendants(window.contentItem()) if i.property("target") is not None]
    overflow = [(r.height(), r.property("implicitHeight")) for r in rows]
    OUTPUT.mkdir(parents=True, exist_ok=True)
    assert window.grabWindow().save(str(OUTPUT / "long-names.png"))
    assert rows and all(actual >= needed - 1 for actual, needed in overflow), overflow


def main():
    QQuickStyle.setStyle("Basic")
    application = QGuiApplication([])
    QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
    application.setFont(QFont("Segoe UI"))
    engine, warnings = QQmlApplicationEngine(), []
    engine.warnings.connect(lambda errors: warnings.extend(e.toString() for e in errors))
    url = QUrl.fromLocalFile(str(Path(app.__file__).parent / "qml/PolicyProbe.qml"))
    engine.loadData(QML, url)
    assert engine.rootObjects(), warnings
    inspect(engine)
    assert not warnings, warnings
    engine.rootObjects()[0].close()


if __name__ == "__main__":
    main()
