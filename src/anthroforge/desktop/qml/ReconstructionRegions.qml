import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: pane
    readonly property var service: workspace.reconstructionPanel
    readonly property var records: JSON.parse(service.dataJson)
    property string selected: ""
    UiButton { text: "Mark a region on selected anatomy"; Layout.fillWidth: true; enabled: !!workspace.selectedId; onClicked: workspace.reconstructionCompare.inspect(workspace.selectedId) }
    UiField { id: search; Layout.fillWidth: true; placeholderText: "Search surface regions" }
    ListView {
        Layout.fillWidth: true; Layout.fillHeight: true; clip: true; reuseItems: true
        model: (pane.records.regions || []).filter(r=>r.name.toLowerCase().includes(search.text.toLowerCase()))
        delegate: ItemDelegate {
            required property var modelData
            width: ListView.view.width; highlighted: pane.selected===modelData.id
            onClicked: pane.selected=modelData.id
            onDoubleClicked: workspace.reconstructionCompare.inspectRegion(modelData.id)
            contentItem: Label { text: modelData.name+" · "+modelData.triangles.length+" faces"; color: Theme.text; wrapMode: Text.Wrap }
            background: Rectangle { color: parent.highlighted ? Theme.selection : parent.hovered ? Theme.hover : "transparent" }
        }
        ScrollBar.vertical: ScrollBar {}
    }
    RowLayout {
        UiButton { text: "View / redefine"; enabled: !!pane.selected; onClicked: workspace.reconstructionCompare.inspectRegion(pane.selected) }
        UiButton { text: "Remove"; enabled: !!pane.selected; onClicked: pane.service.run("catalogue.region.remove",{id:pane.selected}) }
    }
    UiSearchChoice {
        Layout.fillWidth: true; text: "Add region to collection"; enabled: !!pane.selected
        choices: pane.records.detail?.collections || []
        onChosen: row=>pane.service.run("catalogue.collection.set",{collection:row.id,name:row.name,members:row.members.concat([pane.selected])})
    }
}
