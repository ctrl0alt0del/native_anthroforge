import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: pane
    readonly property var service: App.reconstructionPanel
    readonly property var records: JSON.parse(service.dataJson)
    readonly property var catalogue: records.detail || ({})
    property string typeId: ""
    property var collection: ({})
    UiField { id: search; Layout.fillWidth: true; placeholderText: "Search anatomical types" }
    ListView {
        Layout.fillWidth: true; Layout.fillHeight: true; Layout.minimumHeight: 150; clip: true; reuseItems: true
        model: (pane.catalogue.types || []).filter(r=>(r.name+" "+r.aliases.join(" ")).toLowerCase().includes(search.text.toLowerCase()))
        delegate: ItemDelegate {
            required property var modelData
            width: ListView.view.width; highlighted: pane.typeId===modelData.id
            onClicked: { pane.typeId=modelData.id; name.text=modelData.name; category.text=modelData.category; aliases.text=modelData.aliases.join(", "); description.text=modelData.description; }
            contentItem: Label { text: modelData.name; color: Theme.text; wrapMode: Text.Wrap }
            background: Rectangle { color: parent.highlighted ? Theme.selection : parent.hovered ? Theme.hover : "transparent" }
        }
        ScrollBar.vertical: ScrollBar {}
    }
    UiField { id: name; Layout.fillWidth: true; placeholderText: "Type name" }
    UiField { id: category; Layout.fillWidth: true; placeholderText: "Category (optional)" }
    UiField { id: aliases; Layout.fillWidth: true; placeholderText: "Alternative names, separated by commas" }
    UiTextArea { id: description; Layout.fillWidth: true; Layout.preferredHeight: 70; placeholderText: "Description" }
    RowLayout {
        UiButton { text: "New type"; enabled: !!name.text.trim(); onClicked: pane.service.run("catalogue.type.create",{name:name.text,category:category.text.trim() || "OTHER",aliases:aliases.text.split(",").map(s=>s.trim()).filter(Boolean),description:description.text}) }
        UiButton { text: "Update"; enabled: !!pane.typeId && !!name.text.trim(); onClicked: pane.service.run("catalogue.type.update",{type_id:pane.typeId,changes:{name:name.text,category:category.text.trim() || "OTHER",aliases:aliases.text.split(",").map(s=>s.trim()).filter(Boolean),description:description.text}}) }
        UiButton { text: "Delete"; enabled: !!pane.typeId; onClicked: pane.service.run("catalogue.type.remove",{type_id:pane.typeId}) }
    }
    Rectangle { Layout.fillWidth: true; implicitHeight: 1; color: Theme.border }
    Label { text: "Selected anatomy"; color: Theme.text; font.bold: true }
    RowLayout {
        UiCombo { id: side; Layout.fillWidth: true; model: ["Unspecified","Left","Right","Midline"] }
        UiButton { text: "Assign type"; enabled: !!pane.typeId && App.selection.selectedObjects.length>0; onClicked: pane.service.assignSelection(pane.typeId,side.currentText.toUpperCase()) }
        UiButton { text: "Clear"; enabled: App.selection.selectedObjects.length>0; onClicked: pane.service.assignSelection("","UNSPECIFIED") }
    }
    Label { Layout.fillWidth: true; color: Theme.muted; wrapMode: Text.Wrap; text: (pane.catalogue.assignments || []).filter(r=>App.selection.selectedObjects.includes(r.target)).map(r=>(pane.catalogue.types || []).find(t=>t.id===r.type_id)?.name+" · "+r.side).join("\n") }
    UiField { placeholderText: "Instance label"; Layout.fillWidth: true; enabled: App.selection.selectedObjects.length===1; text: (pane.catalogue.assignments || []).find(r=>r.target===App.selection.selectedId)?.label || ""; onEditingFinished: {const a=(pane.catalogue.assignments || []).find(r=>r.target===App.selection.selectedId); if(a) pane.service.run("catalogue.assign",{target:a.target,type_id:a.type_id,side:a.side,label:text,variant:pane.records.active});} }
    UiField { id: collectionName; Layout.fillWidth: true; placeholderText: "Collection name" }
    UiButton { text: "Collect selected anatomy"; Layout.fillWidth: true; enabled: !!collectionName.text.trim() && App.selection.selectedObjects.length>0; onClicked: pane.service.run("catalogue.collection.set",{name:collectionName.text,members:App.selection.selectedObjects}) }
    UiSearchChoice { Layout.fillWidth: true; text: pane.collection.name || "Find a collection"; choices: pane.catalogue.collections || []; onChosen: row=>{pane.collection=row; collectionName.text=row.name; pane.service.selectMembers(row.members);} }
    RowLayout {
        UiButton { text: "Rename"; enabled: !!pane.collection.id && !!collectionName.text.trim(); onClicked: pane.service.run("catalogue.collection.set",{collection:pane.collection.id,name:collectionName.text,members:pane.collection.members}) }
        UiButton { text: "Replace members"; enabled: !!pane.collection.id; hint: "Use the current anatomical selection as this collection's members"; onClicked: pane.service.run("catalogue.collection.set",{collection:pane.collection.id,name:collectionName.text,members:App.selection.selectedObjects}) }
        UiButton { text: "Remove"; enabled: !!pane.collection.id; onClicked: {pane.service.run("catalogue.collection.remove",{id:pane.collection.id});pane.collection={};} }
    }
}
