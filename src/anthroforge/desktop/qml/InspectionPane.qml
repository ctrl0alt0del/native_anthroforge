import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiScrollView {
    id: pane
    contentWidth:availableWidth; clip:true
    ColumnLayout {
        width:pane.availableWidth; spacing:Theme.gap
        UiButton { text:"Inspect neighborhood"; Layout.fillWidth:true; enabled:!!App.selection.selectedId && !App.runtime.state.waiting; hint:"Show this object, its sources, supports and attachments. Restore returns to the previous view."; onClicked:App.neighborhoodView.inspect() }
        UiButton { text:"Restore previous view"; Layout.fillWidth:true; visible:App.neighborhoodView.state.active; onClicked:App.neighborhoodView.restore() }
        UiButton { text:"Check geometry"; Layout.fillWidth:true; visible:!!App.selection.selectedId && !App.selection.selectedData.is_tissue; enabled:App.spatialEvidence.state.available; hint:enabled ? "Check the accepted surface for crossings and degenerate faces. Results are advisory." : App.spatialEvidence.state.reason; onClicked:App.spatialEvidence.check(App.selection.selectedId,"final") }
        UiButton { text:"Hide finding"; Layout.fillWidth:true; visible:App.spatialEvidence.state.active; onClicked:App.spatialEvidence.clear() }
        SurfaceMeasurements { visible:App.spatialEvidence.state.available }
        TissueSections { visible:App.spatialEvidence.state.available && !App.selection.selectedData.is_tissue }
        PlacementInspection {}
        TissueInspection { visible:!!App.selection.selectedData.is_tissue; expanded:true; stateKey:"inspect/tissue" }
        DependencyInspector { visible:!!App.selection.selectedId; expanded:true; stateKey:"inspect/dependencies" }
        Label { visible:!App.selection.selectedId; text:"Select an object to inspect its result and relationships."; color:Theme.muted; Layout.fillWidth:true; wrapMode:Text.Wrap }
    }
}
