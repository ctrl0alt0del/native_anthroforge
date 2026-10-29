import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

UiDialog {
    id: dialog
    property var service: workspace.reconstructionCompare
    title: "Reconstruction comparison"; modal: false; anchors.centerIn: parent
    width: Math.min(1380,parent.width-28); height: Math.min(900,parent.height-28)
    onClosed: service.cancel()
    Connections { target: dialog.service; function onRequested() { dialog.open(); } }
    contentItem: ColumnLayout {
        RowLayout {
            Layout.fillWidth: true
            UiSearchChoice { Layout.fillWidth: true; choices: dialog.service.state.options; text: dialog.service.state.selections[0]?.name || "Before"; onChosen: row=>dialog.service.choose(0,row) }
            UiSearchChoice { Layout.fillWidth: true; choices: dialog.service.state.options; text: dialog.service.state.selections[1]?.name || "After"; onChosen: row=>dialog.service.choose(1,row) }
        }
        RowLayout {
            UiCombo { model: ["Split","Before","After","Overlay"]; onActivated: dialog.service.comparison.setMode(currentText) }
            UiButton { text: "Frame all"; onClicked: dialog.service.comparison.focus("") }
            UiButton { text: "Refresh"; onClicked: dialog.service.submit() }
            UiButton { text: "Export evidence…"; onClicked: evidence.open() }
            UiCheck { id: cut; text: "Section"; onClicked: dialog.updateSection() }
            UiCombo { id: axis; model: ["X","Y","Z"]; enabled: cut.checked; onActivated: dialog.updateSection() }
            NumericSetting { id: position; label: "Position"; value: 0; enabled: cut.checked; length: true; onEdited: v=>{ dialog.cutPosition=v; dialog.updateSection(); } }
            UiCheck { id: flip; text: "Flip"; enabled: cut.checked; onClicked: dialog.updateSection() }
        }
        RowLayout {
            Layout.fillWidth: true; Layout.fillHeight: true
            SkeletonViewport { Layout.fillWidth: true; Layout.fillHeight: true; service: dialog.service.comparison; side: 0; visible: ["Split","Before"].includes(service.state.mode) }
            SkeletonViewport { Layout.fillWidth: true; Layout.fillHeight: true; service: dialog.service.comparison; side: 1; visible: service.state.mode!=="Before"; overlay: service.state.mode==="Overlay" }
        }
        RowLayout {
            UiButton { text: "Mark region in left view"; onClicked: dialog.service.comparison.selectRegion(0) }
            UiButton { text: "Mark region in right view"; onClicked: dialog.service.comparison.selectRegion(1) }
            UiField { id: region; placeholderText: "Region name"; Layout.fillWidth: true; enabled: !!dialog.service.comparison.state.region?.active }
            UiButton { text: (dialog.service.state.region ? "Redefine region (" : "Save region (")+(dialog.service.comparison.state.region?.count || 0)+")"; enabled: !!region.text.trim() && dialog.service.comparison.state.region?.count>0; onClicked: dialog.service.saveRegion(region.text) }
            UiButton { text: "Cancel selection"; enabled: !!dialog.service.comparison.state.region?.active; onClicked: dialog.service.comparison.selectRegion(-1) }
        }
        Label {
            Layout.fillWidth: true; Layout.minimumHeight: 56; Layout.maximumHeight: 56; wrapMode: Text.Wrap; color: Theme.muted
            text: dialog.service.state.error || (dialog.service.state.report.distances ? "Sampled geometric distance: mean "+(dialog.service.state.report.distances.geometric.mean*1000).toFixed(3)+" mm, maximum "+(dialog.service.state.report.distances.geometric.maximum*1000).toFixed(3)+" mm. "+(dialog.service.state.report.distances.material ? "Verified material correspondence available." : "Material correspondence is not established.") : "Frozen accepted stages. Refresh to include later edits.")
        }
    }
    property real cutPosition: 0
    FileDialog { id: evidence; title: "Export reconstruction evidence"; fileMode: FileDialog.SaveFile; defaultSuffix: "afinspection.zip"; nameFilters: ["Inspection evidence (*.afinspection.zip)"]; onAccepted: dialog.service.export(selectedFile.toString()) }
    function updateSection() { service.section(cut.checked,axis.currentIndex,cutPosition,flip.checked); }
}
