import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

RowLayout {
    id: link
    required property string targetId
    required property string label
    Layout.fillWidth: true
    Label { text: link.label; Layout.fillWidth: true; elide: Text.ElideMiddle; color: Theme.text; ToolTip.visible: mouse.containsMouse; ToolTip.text: link.label; MouseArea { id: mouse; anchors.fill: parent; hoverEnabled: true; acceptedButtons: Qt.NoButton } }
    UiButton { objectName: "relatedSelect_"+link.targetId; text: "Select"; enabled: !workspace.state.editing && !workspace.state.waiting; onClicked: workspace.inspectionPanel.navigate(link.targetId,false) }
    UiButton { glyph: "frame"; hint: "Select and frame related object"; enabled: !workspace.state.editing && !workspace.state.waiting; onClicked: workspace.inspectionPanel.navigate(link.targetId,true) }
}
