import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

ColumnLayout {
    required property var keyboard
    readonly property bool dialogVisible: imageFile.visible
    spacing: Theme.gap
    RowLayout {
        Label { text: "CONSTRUCTION"; color: Theme.muted; font.pixelSize: 11; Layout.fillWidth: true }
        UiButton { glyph: "plus"; hint: "Create curves or place the 3D cursor"; onClicked: createMenu.open() }
        UiButton { text: "Image…"; hint: "Import a world reference image"; onClicked: imageFile.open() }
    }
    ListView {
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
    FileDialog { id: imageFile; title: "Import reference image"; nameFilters: ["Reference images (*.png *.jpg *.jpeg)"]; onAccepted: workspace.imageTools.importFile(selectedFile.toString(),false) }
    UiMenu {
        id: createMenu
        UiMenuItem { text: "Add Curve at cursor"; onTriggered: workspace.drawingTools.addCurve() }
        UiMenuItem { text: "Place curve points"; onTriggered: workspace.drawingTools.begin("POINTS") }
        UiMenuItem { text: "Draw curves"; onTriggered: workspace.drawingTools.begin("DRAW") }
        MenuSeparator {}
        UiMenuItem { text: "3D cursor settings"; onTriggered: workspace.drawingTools.begin("CURSOR") }
    }
}
