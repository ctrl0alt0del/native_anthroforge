import QtQuick
import QtQuick.Controls

UiButton {
    property string explanation: ""
    text: "?"; flatStyle: true
    implicitWidth: 24; implicitHeight: 24
    Accessible.name: explanation
    ToolTip.text: explanation
    ToolTip.visible: hovered || activeFocus || down
    ToolTip.delay: 300
    onClicked: ToolTip.show(explanation, 8000)
}
