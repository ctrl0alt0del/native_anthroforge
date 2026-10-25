import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiScrollView {
    id: pane
    contentWidth:availableWidth; clip:true
    ColumnLayout {
        width:pane.availableWidth; spacing:Theme.gap
        TissueInspection { visible:!!workspace.selectedData.is_tissue; expanded:true; stateKey:"inspect/tissue" }
        DependencyInspector { visible:!!workspace.selectedId; expanded:true; stateKey:"inspect/dependencies" }
        Label { visible:!workspace.selectedId; text:"Select an object to inspect its result and relationships."; color:Theme.muted; Layout.fillWidth:true; wrapMode:Text.Wrap }
    }
}
