import QtQuick
import QtQuick.Controls

TextField {
    id: control
    implicitHeight: Theme.controlHeight
    leftPadding: 9; rightPadding: 9
    font.pixelSize: 12
    color: enabled ? Theme.text : Theme.muted
    placeholderTextColor: Theme.muted
    selectionColor: Theme.selection
    selectedTextColor: Theme.text
    selectByMouse: true
    background: Rectangle {
        radius: 4; color: Theme.field
        border.color: control.activeFocus ? Theme.accent : control.hovered ? "#64666f" : Theme.border
    }
}
