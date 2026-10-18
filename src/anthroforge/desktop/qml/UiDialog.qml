import QtQuick
import QtQuick.Controls

Dialog {
    id: dialog
    padding: 16
    background: Rectangle { color: Theme.panel; border.color: Theme.border; radius: 6 }
    header: Label { text: dialog.title; visible: !!text; padding: 16; bottomPadding: 12; font.pixelSize: 15; font.bold: true; color: Theme.text }
}
