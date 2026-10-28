import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiScrollView {
    id: pane
    contentWidth:availableWidth; clip:true
    ColumnLayout {
        width:pane.availableWidth; spacing:Theme.gap
        UiButton { text:"Check geometry"; Layout.fillWidth:true; visible:!!workspace.selectedId && !workspace.selectedData.is_tissue; enabled:workspace.spatialEvidence.state.available; hint:enabled ? "Check the accepted surface for crossings and degenerate faces. Results are advisory." : workspace.spatialEvidence.state.reason; onClicked:workspace.spatialEvidence.check(workspace.selectedId,"final") }
        UiButton { text:"Hide finding"; Layout.fillWidth:true; visible:workspace.spatialEvidence.state.active; onClicked:workspace.spatialEvidence.clear() }
        TissueInspection { visible:!!workspace.selectedData.is_tissue; expanded:true; stateKey:"inspect/tissue" }
        DependencyInspector { visible:!!workspace.selectedId; expanded:true; stateKey:"inspect/dependencies" }
        Label { visible:!workspace.selectedId; text:"Select an object to inspect its result and relationships."; color:Theme.muted; Layout.fillWidth:true; wrapMode:Text.Wrap }
    }
}
