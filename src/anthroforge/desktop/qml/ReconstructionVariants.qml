import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: pane
    readonly property var service: workspace.reconstructionPanel
    readonly property var records: JSON.parse(service.dataJson)
    property string selected: ""
    readonly property var selectedRecord: (records.variants || []).find(r=>r.id===selected)
    readonly property bool mutableSelection: !!selectedRecord && !selectedRecord.checkpoint
    spacing: Theme.gap
    Label { text: pane.records.active ? "Editing variant" : "Accepted anatomy"; color: Theme.accent; Layout.fillWidth: true; wrapMode: Text.WordWrap }
    UiButton { objectName: "newVariant"; text: "Create variant from selection"; Layout.fillWidth: true; enabled: !workspace.state.editing && !workspace.state.waiting && workspace.selectedObjects.length > 0; onClicked: service.create() }
    UiButton { text: "Return to accepted anatomy"; visible: !!pane.records.active; Layout.fillWidth: true; enabled: !workspace.state.editing; onClicked: service.run("variant.leave",{}) }
    UiField { id: search; placeholderText: "Find variants and checkpoints"; Layout.fillWidth: true }
    ListView {
        id: variants; objectName: "variantList"
        Layout.fillHeight: true; Layout.fillWidth: true; Layout.minimumHeight: 150
        clip: true; reuseItems: true
        model: (pane.records.variants || []).filter(row => row.name.toLowerCase().includes(search.text.toLowerCase()))
        delegate: ItemDelegate {
            required property var modelData
            width: ListView.view.width; highlighted: pane.selected === modelData.id
            text: modelData.name + (modelData.checkpoint ? " · checkpoint" : modelData.outdated ? " · supports changed" : "")
            onClicked: { pane.selected=modelData.id; rename.text=modelData.name; }
            onDoubleClicked: service.run(modelData.checkpoint ? "variant.fork" : "variant.enter", {variant:modelData.id})
            contentItem: Label { text: parent.text; wrapMode: Text.WordWrap; color: Theme.text }
            background: Rectangle { color: parent.highlighted ? Theme.selection : parent.hovered ? Theme.hover : "transparent" }
        }
        ScrollBar.vertical: ScrollBar {}
    }
    UiField { id: rename; placeholderText: "Name"; Layout.fillWidth: true; enabled: !!pane.selected; onEditingFinished: if(pane.selected && text.trim()) service.run("variant.rename",{variant:pane.selected,name:text}) }
    RowLayout {
        Layout.fillWidth: true
        UiButton { text: "Edit"; enabled: pane.mutableSelection && !workspace.state.editing; hint: pane.selectedRecord?.checkpoint ? "Fork this checkpoint to edit it" : "Edit with the normal anatomy tools"; onClicked: service.run("variant.enter",{variant:pane.selected}) }
        UiButton { text: "Fork"; enabled: !!pane.selected && !workspace.state.editing; onClicked: service.run("variant.fork",{variant:pane.selected}) }
        UiButton { text: "Checkpoint"; enabled: !!pane.records.active && !workspace.state.editing; onClicked: service.run("variant.checkpoint",{}) }
        UiButton { text: "Remove"; enabled: !!pane.selected && !workspace.state.editing; onClicked: service.run("variant.remove",{variant:pane.selected}) }
    }
    RowLayout {
        Layout.fillWidth: true
        UiButton { text: "Refresh supports"; enabled: pane.mutableSelection; onClicked: workspace.variantPanel.inspect(pane.selected,"refresh") }
        UiButton { text: "Promote"; primary: true; enabled: pane.mutableSelection; onClicked: workspace.variantPanel.inspect(pane.selected,"promote") }
    }
}
