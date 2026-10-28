import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiScrollView {
    id: pane
    contentWidth:availableWidth; clip:true
    ColumnLayout {
        width:pane.availableWidth; spacing:Theme.gap
        UiButton { text:"Inspect neighborhood"; Layout.fillWidth:true; enabled:!!workspace.selectedId && !workspace.state.waiting; hint:"Show this object, its sources, supports and attachments. Restore returns to the previous view."; onClicked:workspace.neighborhoodView.inspect() }
        UiButton { text:"Restore previous view"; Layout.fillWidth:true; visible:workspace.neighborhoodView.state.active; onClicked:workspace.neighborhoodView.restore() }
        UiButton { text:"Check geometry"; Layout.fillWidth:true; visible:!!workspace.selectedId && !workspace.selectedData.is_tissue; enabled:workspace.spatialEvidence.state.available; hint:enabled ? "Check the accepted surface for crossings and degenerate faces. Results are advisory." : workspace.spatialEvidence.state.reason; onClicked:workspace.spatialEvidence.check(workspace.selectedId,"final") }
        UiButton { text:"Hide finding"; Layout.fillWidth:true; visible:workspace.spatialEvidence.state.active; onClicked:workspace.spatialEvidence.clear() }
        SurfaceMeasurements { visible:workspace.spatialEvidence.state.available }
        TissueSections { visible:workspace.spatialEvidence.state.available && !workspace.selectedData.is_tissue }
        PlacementInspection {}
        TissueInspection { visible:!!workspace.selectedData.is_tissue; expanded:true; stateKey:"inspect/tissue" }
        DependencyInspector { visible:!!workspace.selectedId; expanded:true; stateKey:"inspect/dependencies" }
        Label { visible:!workspace.selectedId; text:"Select an object to inspect its result and relationships."; color:Theme.muted; Layout.fillWidth:true; wrapMode:Text.Wrap }
    }
}
