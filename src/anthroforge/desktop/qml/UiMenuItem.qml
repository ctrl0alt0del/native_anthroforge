import QtQuick
import QtQuick.Controls

MenuItem {
    id: control
    objectName: "menuItem" + text
    property string shortcutHint: ""
    property string detail: ""
    property string hint: ""
    implicitHeight: visible ? Math.max(Theme.controlHeight, contentItem.implicitHeight + 10) : 0
    leftPadding: 28; rightPadding: Theme.inset
    hoverEnabled: true
    ToolTip.visible: hovered && !!hint
    ToolTip.text: hint; ToolTip.delay: 500
    contentItem: Item {
        implicitWidth: Math.max(label.implicitWidth + key.implicitWidth + Theme.inset, Math.min(360, description.implicitWidth))
        implicitHeight: label.implicitHeight + (description.visible ? description.implicitHeight + 2 : 0)
        Text { id: label; anchors.left: parent.left; anchors.right: key.left; anchors.rightMargin: Theme.inset; y:(parent.height-parent.implicitHeight)/2; text: control.text; font: control.font; color: control.enabled ? Theme.text : Theme.muted; elide: Text.ElideRight }
        Text { id: key; anchors.right: parent.right; y:label.y; text: control.shortcutHint; font: control.font; color: Theme.muted }
        Text { id: description; visible: !!control.detail; width: parent.width; y:label.y+label.height+2; text:control.detail; font.pixelSize:11; color:Theme.muted; elide:Text.ElideMiddle }
    }
    indicator: Text { x: 8; y: (control.height-height)/2; text: "✓"; visible: control.checked; color: Theme.accent; font.pixelSize: 13 }
    background: Rectangle { radius: Theme.radius; color: control.down ? Theme.selection : control.highlighted || control.hovered ? Theme.hover : "transparent"; border.color: control.activeFocus ? Theme.accent : "transparent" }
}
