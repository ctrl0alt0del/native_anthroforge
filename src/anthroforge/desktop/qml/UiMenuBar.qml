import QtQuick
import QtQuick.Controls

MenuBar {
    background: Item {}
    delegate: MenuBarItem {
        id: control
        objectName: "menuBar" + text
        implicitHeight: Theme.controlHeight
        leftPadding: Theme.inset; rightPadding: Theme.inset
        contentItem: Text { text: control.text; font: control.font; color: Theme.text; verticalAlignment: Text.AlignVCenter }
        background: Rectangle { radius: Theme.radius; color: control.down || control.highlighted ? Theme.hover : "transparent" }
    }
}
