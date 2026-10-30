import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: pane
    readonly property var service: App.reconstructionPanel
    readonly property var records: JSON.parse(service.dataJson)
    readonly property var rows: records.detail?.work || []
    property string selected: ""
    property string checkpoint: ""
    UiField { id: owner; Layout.fillWidth: true; placeholderText: "Your name" }
    RowLayout {
        UiButton { text: "Add selected"; enabled: !!App.selection.selectedId; onClicked: pane.service.run("reconstruction.queue.add",{subject:App.selection.selectedId,variant:pane.records.active}) }
        UiButton { text: "Claim next"; enabled: !!owner.text.trim(); onClicked: {const r=pane.service.run("reconstruction.queue.claim",{owner:owner.text}); if(r?.id) pane.selected=r.id;} }
    }
    UiField { id: search; Layout.fillWidth: true; placeholderText: "Search queue" }
    ListView {
        Layout.fillWidth: true; Layout.fillHeight: true; Layout.minimumHeight: 150; clip: true; reuseItems: true
        model: pane.rows.filter(r=>(r.name+" "+r.owner+" "+r.next_action+" "+r.status).toLowerCase().includes(search.text.toLowerCase()))
        delegate: ItemDelegate {
            required property var modelData
            width: ListView.view.width; highlighted: modelData.id===pane.selected
            onClicked: {pane.selected=modelData.id; pane.checkpoint=modelData.checkpoint; nextAction.text=modelData.next_action; blocker.text=modelData.blocker; approach.text=modelData.approach; status.currentIndex=pane.records.detail.statuses.indexOf(modelData.status);}
            contentItem: Label { color: Theme.text; wrapMode: Text.Wrap; text: (modelData.name || modelData.subject)+"\n"+modelData.status+" · "+(modelData.owner || "Unclaimed") }
            background: Rectangle { color: parent.highlighted ? Theme.selection : parent.hovered ? Theme.hover : "transparent" }
        }
        ScrollBar.vertical: ScrollBar {}
    }
    RowLayout {
        UiButton { text: "Claim"; enabled: !!pane.selected && !!owner.text.trim(); onClicked: pane.service.run("reconstruction.queue.claim",{work:pane.selected,owner:owner.text}) }
        UiButton { text: "Take over"; enabled: !!pane.selected && !!owner.text.trim(); hint: "Explicitly take ownership of this anatomical type and its active work"; onClicked: pane.service.run("reconstruction.queue.claim",{work:pane.selected,owner:owner.text,takeover:true}) }
        UiButton { text: "Open work"; enabled: !!pane.selected; onClicked: pane.service.resumeWork(pane.rows.find(r=>r.id===pane.selected)) }
    }
    UiCombo { id: status; Layout.fillWidth: true; model: pane.records.detail?.statuses || [] }
    UiField { id: nextAction; Layout.fillWidth: true; placeholderText: "Next action" }
    UiField { id: blocker; Layout.fillWidth: true; placeholderText: "Blocker, if any" }
    UiTextArea { id: approach; Layout.fillWidth: true; Layout.preferredHeight: 80; placeholderText: "Approach and handoff notes" }
    UiSearchChoice { Layout.fillWidth: true; choices: [{id:"",name:"No checkpoint"}].concat((pane.records.variants || []).filter(r=>r.checkpoint)); text: choices.find(r=>r.id===pane.checkpoint)?.name || "Choose checkpoint"; onChosen: row=>pane.checkpoint=row.id }
    UiButton { text: "Update work"; Layout.fillWidth: true; enabled: !!pane.selected && !!owner.text.trim(); onClicked: pane.service.run("reconstruction.queue.update",{work:pane.selected,owner:owner.text,status:status.currentText,next_action:nextAction.text,blocker:blocker.text,approach:approach.text,checkpoint:pane.checkpoint}) }
}
