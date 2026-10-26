import QtQuick
import QtQuick.Controls

TabButton {
    id: control
    property string hint: ""
    property bool vertical: false
    implicitHeight: Theme.controlHeight + 4
    padding: Theme.gap
    font.pixelSize: 12
    hoverEnabled: true
    Accessible.name: text
    Accessible.description: hint
    ToolTip.visible: hovered && !!hint
    ToolTip.text: hint
    ToolTip.delay: 500
    contentItem: Item {
        Text {
            anchors.centerIn: parent
            width: control.vertical ? parent.height : parent.width
            height: control.vertical ? parent.width : parent.height
            rotation: control.vertical ? -90 : 0
            text: control.text; font: control.font
            color: control.enabled && (control.checked || control.hovered) ? Theme.text : Theme.muted
            horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
        }
    }
    background: Rectangle {
        color: control.checked ? Theme.panel : control.hovered ? Theme.hover : Theme.field
        Rectangle { width: control.vertical ? 2 : parent.width; height: control.vertical ? parent.height : 2; color: Theme.accent; visible: control.checked }
        Rectangle { width: parent.width; height: 1; anchors.bottom: parent.bottom; color: Theme.border; visible: !control.checked }
        Rectangle { anchors.fill: parent; anchors.margins: 3; color: "transparent"; border.color: Theme.accent; visible: control.visualFocus }
    }
}
