import QtQuick
import QtQuick.Controls

Dialog {
    id: dialog
    padding: 16
    background: Rectangle { color: Theme.panel; border.color: Theme.border; radius: 6 }
    header: Label { text: dialog.title; visible: !!text; padding: 16; bottomPadding: 12; font.pixelSize: 15; font.bold: true; color: Theme.text; wrapMode: Text.Wrap }
    footer: DialogButtonBox {
        visible: count > 0
        padding: 16; spacing: Theme.gap
        alignment: Qt.AlignRight
        delegate: UiButton { implicitWidth: Math.max(88, contentItem.implicitWidth+24) }
        background: Item {}
    }
}
