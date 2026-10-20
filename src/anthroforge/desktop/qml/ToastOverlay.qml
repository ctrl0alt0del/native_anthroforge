import QtQuick
import QtQuick.Controls

Rectangle {
    objectName: "transientNotice"
    parent: Overlay.overlay
    anchors.right: parent.right; anchors.bottom: parent.bottom; anchors.margins: 24
    width: Math.min(420,parent.width-48)
    height: message.implicitHeight+24
    visible: ToastBus.showing
    z: 10; radius: 6; color: Theme.panel; border.color: ToastBus.error ? Theme.danger : Theme.accent
    Label {
        id: message
        anchors.fill: parent; anchors.margins: 12
        text: ToastBus.text; textFormat: Text.PlainText; color: Theme.text; wrapMode: Text.WordWrap
        maximumLineCount: 8; elide: Text.ElideRight
    }
}
