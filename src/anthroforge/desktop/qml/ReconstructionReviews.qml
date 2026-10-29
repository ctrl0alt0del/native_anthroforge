import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

ColumnLayout {
    id: pane
    readonly property var service: workspace.reconstructionPanel
    readonly property var records: JSON.parse(service.dataJson)
    readonly property var detail: records.detail || ({})
    property var reviewStage: ({stage:"final",variant:records.active})
    property var evidenceIds: []
    Label { text: workspace.selectedData.name || "Select anatomy to review"; color: Theme.text; font.bold: true; Layout.fillWidth: true; wrapMode: Text.Wrap }
    UiCombo { id: dimension; Layout.fillWidth: true; model: ["Anatomy","Route / collision","Attachment","Stacking","Persistence","Display"] }
    UiCombo { id: decision; Layout.fillWidth: true; model: ["Pending","Approved","Rejected","Not applicable"] }
    UiSearchChoice { Layout.fillWidth: true; choices: pane.records.reviewStages || []; text: pane.reviewStage.name || "Current final surface"; onChosen: row=>pane.reviewStage=row }
    UiField { id: reviewer; Layout.fillWidth: true; placeholderText: "Reviewer" }
    UiTextArea { id: comment; Layout.fillWidth: true; Layout.preferredHeight: 100; placeholderText: "Review comments" }
    RowLayout {
        UiButton { text: "Add evidence…"; onClicked: evidenceFile.open() }
        UiSearchChoice { Layout.fillWidth: true; text: "Evidence ("+pane.evidenceIds.length+")"; choices: pane.records.evidence || []; onChosen: row=>{ const chosen=pane.evidenceIds.slice(); const i=chosen.indexOf(row.id); if(i<0) chosen.push(row.id); else chosen.splice(i,1); pane.evidenceIds=chosen; } }
    }
    Label { Layout.fillWidth: true; wrapMode: Text.Wrap; color: Theme.muted; text: (pane.records.evidence || []).filter(r=>pane.evidenceIds.includes(r.id)).map(r=>r.name).join(", ") }
    UiButton {
        text: "Record review"; Layout.fillWidth: true; enabled: !!workspace.selectedId && (!!reviewer.text.trim() || decision.currentIndex===0)
        onClicked: pane.service.run("review.set",{subject:workspace.selectedId,dimension:pane.detail.dimensions[dimension.currentIndex],decision:pane.detail.decisions[decision.currentIndex],variant:pane.reviewStage.variant,stage:pane.reviewStage.stage,reviewer:reviewer.text,comment:comment.text,evidence:pane.evidenceIds})
    }
    UiField { id: search; Layout.fillWidth: true; placeholderText: "Search review history" }
    ListView {
        Layout.fillWidth: true; Layout.fillHeight: true; clip: true; reuseItems: true
        model: (pane.detail.reviews || []).filter(r=>(!workspace.selectedId || r.subject===workspace.selectedId) && (r.comment+" "+r.reviewer+" "+r.dimension).toLowerCase().includes(search.text.toLowerCase())).slice().reverse()
        delegate: ColumnLayout {
            required property var modelData
            width: ListView.view.width-14
            Label { Layout.fillWidth: true; color: modelData.freshness==="CURRENT" ? Theme.text : Theme.accent; wrapMode: Text.Wrap; text: modelData.dimension.replaceAll("_"," ")+" · "+modelData.decision.replaceAll("_"," ") }
            Label { Layout.fillWidth: true; color: Theme.muted; wrapMode: Text.Wrap; text: modelData.reviewer+" · "+modelData.freshness }
            Label { Layout.fillWidth: true; color: Theme.text; wrapMode: Text.Wrap; text: modelData.comment }
            Rectangle { Layout.fillWidth: true; implicitHeight: 1; color: Theme.border; Layout.topMargin: 5; Layout.bottomMargin: 5 }
        }
        ScrollBar.vertical: ScrollBar {}
    }
    FileDialog { id: evidenceFile; title: "Embed review evidence"; nameFilters: ["Images and reports (*.png *.jpg *.jpeg *.afinspection.zip *.afprofile.zip)"]; onAccepted: pane.service.importEvidence(selectedFile.toString()) }
}
