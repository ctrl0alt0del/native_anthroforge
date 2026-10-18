import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

ColumnLayout {
    readonly property bool dialogVisible: imageFile.visible
    spacing: Theme.gap
    RowLayout {
        Label { text: "CONSTRUCTION"; color: Theme.muted; font.pixelSize: 11; Layout.fillWidth: true }
        UiButton { glyph: "plus"; hint: "Add an independent curve"; onClicked: {
            const owner=workspace.selectedData.is_construction || workspace.selectedData.is_control ? "" : workspace.selectedId;
            const id=workspace.run("curve.create",{owner:owner});
            if(id) { workspace.select(id); authoring.setEditing(true); }
        } }
        UiButton { text: "Image…"; hint: "Import a world reference image"; onClicked: imageFile.open() }
    }
    ListView {
        Layout.fillWidth: true; Layout.fillHeight: true; clip: true
        model: workspace.constructionModel
        ScrollBar.vertical: ScrollBar {}
        delegate: Rectangle {
            required property var item
            width: ListView.view.width; height: 46
            color: workspace.selectedId === item.id ? Theme.selection : pointer.containsMouse ? Theme.hover : "transparent"
            Column {
                anchors.left: parent.left; anchors.right: parent.right; anchors.margins: Theme.inset
                anchors.verticalCenter: parent.verticalCenter; spacing: 2
                Label { text: item.name; color: item.readonly ? Theme.muted : Theme.text; width: parent.width; elide: Text.ElideRight }
                Label { text: item.kind.toLowerCase() + (item.unassigned ? " · unassigned" : "") + (item.status === "pending" ? " · pending" : ""); color: Theme.muted; font.pixelSize: 10 }
            }
            MouseArea { id: pointer; anchors.fill: parent; hoverEnabled: true; onClicked: workspace.select(parent.item.id) }
        }
    }
    FileDialog { id: imageFile; title: "Import reference image"; nameFilters: ["Reference images (*.png *.jpg *.jpeg)"]; onAccepted: workspace.imageTools.importFile(selectedFile.toString(),false) }
}
