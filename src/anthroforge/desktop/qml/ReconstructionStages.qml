import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

ColumnLayout {
    id: pane
    readonly property var service: App.reconstructionPanel
    readonly property var records: JSON.parse(service.dataJson)
    property string sourceEntity: ""
    property var placement: [0,0,0,0,0,0,1,1,1]
    readonly property bool project: (records.source?.path || "").endsWith(".anthroforge")
    Label { text: App.selection.selectedData.name || "Select anatomy"; color: Theme.text; wrapMode: Text.Wrap; Layout.fillWidth: true }
    UiButton { text: "Compare stages and variants"; Layout.fillWidth: true; enabled: !!App.selection.selectedId; onClicked: App.reconstructionCompare.inspect(App.selection.selectedId) }
    UiSection {
        title: "Import reference stage"; expanded: true
        UiCombo { id: stage; model: ["Original reference","Transferred anatomy"]; Layout.fillWidth: true }
        UiButton { text: pane.records.source?.path ? "Choose another file…" : "Choose mesh or project…"; Layout.fillWidth: true; onClicked: file.open() }
        Label { text: pane.records.source?.path || ""; wrapMode: Text.WrapAnywhere; color: Theme.muted; Layout.fillWidth: true }
        UiSearchChoice { visible: pane.project; Layout.fillWidth: true; choices: (pane.records.source?.inventory || []).filter(r=>r.anatomy); text: choices.find(r=>r.id===pane.sourceEntity)?.name || "Choose saved anatomy"; onChosen: row=>pane.sourceEntity=row.id }
        UiCombo { id: role; visible: pane.project; model: ["final","intrinsic","rest","base"]; Layout.fillWidth: true }
        UiCombo { id: units; visible: !pane.project; model: ["Metres","Centimetres","Millimetres"]; Layout.fillWidth: true }
        UiCheck { id: yUp; text: "Source uses Y up"; visible: !pane.project }
        UiSection {
            title: "Placement"; expanded: false
            Repeater { model: ["X","Y","Z","Rotate X","Rotate Y","Rotate Z"]
                NumericSetting { required property int index; required property string modelData; label: modelData; value: pane.placement[index]; length: index<3; onEdited: v=>{ const values=pane.placement.slice(); values[index]=v; pane.placement=values; } }
            }
        }
        UiButton { text: "Import stage"; Layout.fillWidth: true; enabled: !!App.selection.selectedId && !!pane.records.source?.path && (!pane.project || !!pane.sourceEntity); onClicked: pane.service.importStage(stage.currentIndex ? "TRANSFERRED" : "ORIGINAL",[1,.01,.001][units.currentIndex],yUp.checked,pane.placement,pane.sourceEntity,role.currentText) }
    }
    Label { text: "Embedded stages"; color: Theme.text; font.bold: true }
    ListView {
        Layout.fillWidth: true; Layout.fillHeight: true; Layout.minimumHeight: 150; clip: true; reuseItems: true
        model: (pane.records.detail?.stages || []).filter(r=>!App.selection.selectedId || r.subject===App.selection.selectedId)
        delegate: RowLayout {
            required property var modelData; width: ListView.view.width-14
            Label { text: modelData.name || modelData.stage; Layout.fillWidth: true; color: Theme.text; wrapMode: Text.Wrap }
            UiButton { text: "×"; hint: "Remove stage"; onClicked: pane.service.run("reconstruction.stage.remove",{stage:modelData.id}) }
        }
        ScrollBar.vertical: ScrollBar {}
    }
    FileDialog { id: file; title: "Import reconstruction reference"; nameFilters: ["Meshes or projects (*.obj *.stl *.ply *.anthroforge)"]; onAccepted: pane.service.chooseStageFile(selectedFile.toString()) }
}
