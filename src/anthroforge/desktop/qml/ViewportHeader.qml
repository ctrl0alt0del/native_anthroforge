import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: header
    required property var viewport
    signal manageRequested()
    signal imageRequested()
    signal overlaysRequested()
    color:Theme.panel; implicitHeight:layout.implicitHeight+10
    GridLayout {
        id: layout; anchors.fill:parent; anchors.margins:5
        columns:header.width<620 ? 1 : 2; columnSpacing:Theme.gap; rowSpacing:3
        RowLayout {
            Layout.fillWidth:true; spacing:4
            WorkspaceSelector { Layout.fillWidth:true; Layout.minimumWidth:110 }
            UiButton { objectName:"manageWorkspace"; glyph:"more"; hint:"Manage workspaces"; enabled:!App.runtime.state.waiting && !App.runtime.state.editing; onClicked:header.manageRequested() }
            UiButton { objectName:"focusSelection"; glyph:"target"; hint:"Focus selected anatomy and descendants"; enabled:!!App.selection.selectedId && !App.selection.selectedData.is_construction && !App.selection.selectedData.is_control && !App.runtime.state.waiting; onClicked:App.selection.focusSelection() }
        }
        RowLayout {
            Layout.fillWidth:true; spacing:4
            UiButton { objectName:"addWorldImage"; glyph:"image"; flatStyle:true; hint:"Add a world reference image"+(header.viewport.imageAlignmentAxis ? " · "+header.viewport.imageAlignmentAxis+" alignment" : ""); enabled:!App.runtime.state.waiting && !App.runtime.state.editing; onClicked:header.imageRequested() }
            UiButton { text:header.viewport.orthographic ? "Orthographic" : "Perspective"; flatStyle:true; hint:"Switch projection · 5"; onClicked:header.viewport.orthographic=!header.viewport.orthographic }
            UiButton { glyph:"frame"; flatStyle:true; hint:"Frame selected · F"; onClicked:App.viewport.frameSelection() }
            Item { Layout.fillWidth:true }
            UiButton { text:"Overlays"; flatStyle:true; onClicked:header.overlaysRequested() }
        }
    }
}
