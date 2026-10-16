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
    implicitHeight: 28
    implicitWidth: Math.max(28, contentItem.implicitWidth + 18)
    padding: 6
    hoverEnabled: true
    font.pixelSize: 12
    Accessible.name: hint || text
    ToolTip.visible: hovered && !!hint
    ToolTip.text: hint
    ToolTip.delay: 500
    contentItem: RowLayout {
        spacing: 6
        Image { visible: !!control.glyph; source: control.glyph ? "icons/" + control.glyph + ".svg" : ""; sourceSize: Qt.size(16,16); opacity: control.enabled ? 1 : .35 }
        Text { visible: !!control.text; text: control.text; font: control.font; color: control.enabled ? Theme.text : Theme.muted; horizontalAlignment: control.alignLeft ? Text.AlignLeft : Text.AlignHCenter; Layout.fillWidth: true }
    }
    background: Rectangle {
        radius: 4
        color: control.down ? Theme.selection : control.checked ? Theme.selection : control.hovered ? Theme.hover : control.primary ? "#574333" : control.flatStyle ? "transparent" : Theme.header
        border.color: control.activeFocus || control.checked || control.primary ? Theme.accent : control.flatStyle ? "transparent" : Theme.border
        opacity: control.enabled ? 1 : .45
    }
}
