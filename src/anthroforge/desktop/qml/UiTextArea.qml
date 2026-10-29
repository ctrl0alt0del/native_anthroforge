import QtQuick
import QtQuick.Controls

TextArea {
    id: control
    color: enabled ? Theme.text : Theme.muted
    placeholderTextColor: Theme.muted
    selectionColor: Theme.selection; selectedTextColor: Theme.text
    selectByMouse: true; wrapMode: TextEdit.Wrap
    padding: 9; font.pixelSize: 12
    background: Rectangle { color: Theme.field; radius: Theme.radius; border.color: control.activeFocus ? Theme.accent : Theme.border }
}
