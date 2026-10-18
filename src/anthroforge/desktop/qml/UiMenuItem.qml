import QtQuick
import QtQuick.Controls

MenuItem {
    id: control
    objectName: "menuItem" + text
    property string shortcutHint: ""
    implicitHeight: Theme.controlHeight
    leftPadding: 28; rightPadding: Theme.inset
    hoverEnabled: true
    contentItem: Item {
        implicitWidth: label.implicitWidth + key.implicitWidth + Theme.inset
        implicitHeight: label.implicitHeight
        Text { id: label; anchors.left: parent.left; anchors.right: key.left; anchors.rightMargin: Theme.inset; anchors.verticalCenter: parent.verticalCenter; text: control.text; font: control.font; color: control.enabled ? Theme.text : Theme.muted; elide: Text.ElideRight }
        Text { id: key; anchors.right: parent.right; anchors.verticalCenter: parent.verticalCenter; text: control.shortcutHint; font: control.font; color: Theme.muted }
    }
    indicator: Text { x: 8; y: (control.height-height)/2; text: "✓"; visible: control.checked; color: Theme.accent; font.pixelSize: 13 }
    background: Rectangle { radius: Theme.radius; color: control.down ? Theme.selection : control.highlighted || control.hovered ? Theme.hover : "transparent"; border.color: control.activeFocus ? Theme.accent : "transparent" }
}
