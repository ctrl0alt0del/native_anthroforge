import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    required property var keyboard
    spacing: Theme.gap
    SurfacePreview {}
    ListView {
        objectName: "constructionList"
        Layout.fillWidth: true; Layout.fillHeight: true; clip: true
        model: workspace.constructionModel
        ScrollBar.vertical: ScrollBar {}
        delegate: Rectangle {
            required property var item
            width: ListView.view.width; height: 46
            color: workspace.selectedObjects.includes(item.id) ? Theme.selection : pointer.containsMouse ? Theme.hover : "transparent"
            Column {
                anchors.left: parent.left; anchors.right: parent.right; anchors.margins: Theme.inset
                anchors.verticalCenter: parent.verticalCenter; spacing: 2
                Label { text: item.name; color: item.readonly ? Theme.muted : Theme.text; width: parent.width; elide: Text.ElideRight }
                Label { text: item.kind.toLowerCase() + (item.unassigned ? " · unassigned" : "") + (item.status === "pending" ? " · pending" : ""); color: Theme.muted; font.pixelSize: 10 }
            }
            MouseArea { id: pointer; anchors.fill: parent; hoverEnabled: true; onClicked: mouse => workspace.select(parent.item.id,keyboard.matches("extendSelection",mouse.modifiers)) }
        }
    }
}
