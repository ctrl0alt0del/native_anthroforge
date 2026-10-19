import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Button {
    id: control
    property string glyph: ""
    property string hint: ""
    property bool primary: false
    property bool flatStyle: false
    property bool alignLeft: false
    implicitHeight: Theme.controlHeight
    implicitWidth: Math.max(28, contentItem.implicitWidth + 18)
    // Compact callers keep the same content size; padding yields before content clips.
    horizontalPadding: Math.min(Theme.gap, Math.max(0, (width - implicitContentWidth) / 2))
    verticalPadding: Math.min(6, Math.max(0, (height - implicitContentHeight) / 2))
    hoverEnabled: true
    font.pixelSize: 12
    Accessible.name: hint || text
    ToolTip.visible: hovered && !!hint
    ToolTip.text: hint
    ToolTip.delay: 500
    contentItem: Item {
        implicitWidth: (icon.visible ? 16 : 0) + (label.visible ? label.implicitWidth : 0) + (icon.visible && label.visible ? 6 : 0)
        implicitHeight: Math.max(icon.visible ? 16 : 0, label.visible ? label.implicitHeight : 0)
        RowLayout {
            width: Math.min(parent.width, parent.implicitWidth); height: parent.height
            x: control.alignLeft ? 0 : (parent.width - width) / 2
            spacing: 6
            Image {
                id: icon
                visible: !!control.glyph
                source: control.glyph ? "icons/" + control.glyph + ".svg" : ""
                sourceSize: Qt.size(16,16)
                Layout.preferredWidth: 16; Layout.preferredHeight: 16
                opacity: control.enabled ? 1 : .35
            }
            Text {
                id: label
                visible: !!control.text; text: control.text; font: control.font
                color: control.enabled ? Theme.text : Theme.muted
                horizontalAlignment: control.alignLeft ? Text.AlignLeft : Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                Layout.fillWidth: true; Layout.minimumWidth: 0
                elide: Text.ElideRight
            }
        }
    }
    background: Rectangle {
        radius: 4
        color: control.down ? Theme.selection : control.checked ? Theme.selection : control.hovered ? Theme.hover : control.primary ? "#574333" : control.flatStyle ? "transparent" : Theme.header
        border.color: control.activeFocus || control.checked || control.primary ? Theme.accent : control.flatStyle ? "transparent" : Theme.border
        opacity: control.enabled ? 1 : .45
    }
}
