import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: pane
    readonly property var service: workspace.reconstructionPanel
    readonly property var records: JSON.parse(service.dataJson)
    readonly property var catalogue: records.detail || ({})
    property string typeId: ""
    UiField { id: search; Layout.fillWidth: true; placeholderText: "Search anatomical types" }
    ListView {
        Layout.fillWidth: true; Layout.fillHeight: true; clip: true; reuseItems: true
        model: (pane.catalogue.types || []).filter(r=>(r.name+" "+r.aliases.join(" ")).toLowerCase().includes(search.text.toLowerCase()))
        delegate: ItemDelegate {
            required property var modelData
            width: ListView.view.width; highlighted: pane.typeId===modelData.id
            onClicked: { pane.typeId=modelData.id; name.text=modelData.name; aliases.text=modelData.aliases.join(", "); description.text=modelData.description; }
            contentItem: Label { text: modelData.name; color: Theme.text; wrapMode: Text.Wrap }
            background: Rectangle { color: parent.highlighted ? Theme.selection : parent.hovered ? Theme.hover : "transparent" }
        }
        ScrollBar.vertical: ScrollBar {}
    }
    UiField { id: name; Layout.fillWidth: true; placeholderText: "Type name" }
    UiField { id: aliases; Layout.fillWidth: true; placeholderText: "Alternative names, separated by commas" }
    UiTextArea { id: description; Layout.fillWidth: true; Layout.preferredHeight: 70; placeholderText: "Description" }
    RowLayout {
        UiButton { text: "New type"; enabled: !!name.text.trim(); onClicked: pane.service.run("catalogue.type.create",{name:name.text,aliases:aliases.text.split(",").map(s=>s.trim()).filter(Boolean),description:description.text}) }
        UiButton { text: "Update"; enabled: !!pane.typeId && !!name.text.trim(); onClicked: pane.service.run("catalogue.type.update",{type_id:pane.typeId,changes:{name:name.text,aliases:aliases.text.split(",").map(s=>s.trim()).filter(Boolean),description:description.text}}) }
        UiButton { text: "Delete"; enabled: !!pane.typeId; onClicked: pane.service.run("catalogue.type.remove",{type_id:pane.typeId}) }
    }
    Rectangle { Layout.fillWidth: true; implicitHeight: 1; color: Theme.border }
    Label { text: "Selected anatomy"; color: Theme.text; font.bold: true }
    RowLayout {
        UiCombo { id: side; Layout.fillWidth: true; model: ["Unspecified","Left","Right","Midline"] }
        UiButton { text: "Assign type"; enabled: !!pane.typeId && workspace.selectedObjects.length>0; onClicked: pane.service.assignSelection(pane.typeId,side.currentText.toUpperCase()) }
        UiButton { text: "Clear"; enabled: workspace.selectedObjects.length>0; onClicked: pane.service.assignSelection("","UNSPECIFIED") }
    }
    Label { Layout.fillWidth: true; color: Theme.muted; wrapMode: Text.Wrap; text: (pane.catalogue.assignments || []).filter(r=>workspace.selectedObjects.includes(r.target)).map(r=>(pane.catalogue.types || []).find(t=>t.id===r.type_id)?.name+" · "+r.side).join("\n") }
    UiField { id: collectionName; Layout.fillWidth: true; placeholderText: "Collection name" }
    UiButton { text: "Collect selected anatomy"; Layout.fillWidth: true; enabled: !!collectionName.text.trim() && workspace.selectedObjects.length>0; onClicked: pane.service.run("catalogue.collection.set",{name:collectionName.text,members:workspace.selectedObjects}) }
    UiSearchChoice { Layout.fillWidth: true; text: "Find a collection"; choices: pane.catalogue.collections || []; onChosen: row=>pane.service.selectMembers(row.members) }
}
