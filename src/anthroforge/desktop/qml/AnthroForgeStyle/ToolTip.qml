import QtQuick
import QtQuick.Templates as T
import ".." as Ui

T.ToolTip {
    id: control
    objectName: "applicationToolTip"
    readonly property real widthLimit: Math.min(380, parent && parent.Window.window ? parent.Window.window.width-24 : 380)
    x: parent ? (parent.width-width)/2 : 0
    y: -implicitHeight-8
    implicitWidth: Math.min(widthLimit, metrics.boundingRect.width+leftPadding+rightPadding)
    implicitHeight: contentItem.implicitHeight+topPadding+bottomPadding
    padding: 10; margins: 8
    font.pixelSize: 12
    closePolicy: T.Popup.CloseOnEscape | T.Popup.CloseOnPressOutsideParent | T.Popup.CloseOnReleaseOutsideParent
    TextMetrics { id: metrics; text: control.text; font: control.font }
    contentItem: Text {
        text: control.text; textFormat: Text.PlainText; font: control.font
        wrapMode: Text.Wrap; color: Ui.Theme.text; lineHeight: 1.25
    }
    background: Rectangle { color: Ui.Theme.header; border.color: Ui.Theme.border; radius: 3 }
}
