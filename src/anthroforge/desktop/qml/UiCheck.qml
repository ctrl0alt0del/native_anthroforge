import QtQuick
import QtQuick.Controls

CheckBox {
    id: control
    property string hint: ""
    ToolTip.text: hint
    ToolTip.visible: hovered && hint.length > 0
    ToolTip.delay: 700
    implicitWidth: text ? contentItem.implicitWidth : indicator.width
    implicitHeight: Math.max(Theme.controlHeight, contentItem.implicitHeight); padding: 0
    spacing: 8
    font.pixelSize: 12
    indicator: Rectangle {
        x: 0; y: (control.height-height)/2; width: 16; height: 16; radius: 3
        color: control.checked ? Theme.selection : Theme.field
        border.color: control.checked || control.activeFocus ? Theme.accent : Theme.border
        Text { anchors.centerIn: parent; text: "✓"; visible: control.checked; color: Theme.accent; font.pixelSize: 12 }
    }
    contentItem: Text { leftPadding: control.text ? 24 : 0; text: control.text; font: control.font; color: control.enabled ? Theme.text : Theme.muted; verticalAlignment: Text.AlignVCenter; wrapMode: Text.Wrap }
}
