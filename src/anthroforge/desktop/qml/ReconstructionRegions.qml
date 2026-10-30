import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: pane
    readonly property var service: App.reconstructionPanel
    readonly property var records: JSON.parse(service.dataJson)
    property string selected: ""
    UiButton { text: "Mark a region on selected anatomy"; Layout.fillWidth: true; enabled: !!App.selection.selectedId; onClicked: App.reconstructionCompare.inspect(App.selection.selectedId) }
    UiField { id: search; Layout.fillWidth: true; placeholderText: "Search surface regions" }
    ListView {
        Layout.fillWidth: true; Layout.fillHeight: true; Layout.minimumHeight: 150; clip: true; reuseItems: true
        model: (pane.records.regions || []).filter(r=>r.name.toLowerCase().includes(search.text.toLowerCase()))
        delegate: ItemDelegate {
            required property var modelData
            width: ListView.view.width; highlighted: pane.selected===modelData.id
            onClicked: pane.selected=modelData.id
            onDoubleClicked: App.reconstructionCompare.inspectRegion(modelData.id)
            contentItem: Label { text: modelData.name+" · "+modelData.triangles.length+" faces"; color: Theme.text; wrapMode: Text.Wrap }
            background: Rectangle { color: parent.highlighted ? Theme.selection : parent.hovered ? Theme.hover : "transparent" }
        }
        ScrollBar.vertical: ScrollBar {}
    }
    RowLayout {
        UiButton { text: "View / redefine"; enabled: !!pane.selected; onClicked: App.reconstructionCompare.inspectRegion(pane.selected) }
        UiButton { text: "Remove"; enabled: !!pane.selected; onClicked: pane.service.run("catalogue.region.remove",{id:pane.selected}) }
    }
    UiSearchChoice {
        Layout.fillWidth: true; text: "Add region to collection"; enabled: !!pane.selected
        choices: pane.records.detail?.collections || []
        onChosen: row=>pane.service.run("catalogue.collection.set",{collection:row.id,name:row.name,members:row.members.concat([pane.selected])})
    }
}
