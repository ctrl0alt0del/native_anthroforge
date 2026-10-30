import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    readonly property var preview: App.construction.surfacePreview
    visible: preview.state!=="idle"
    Layout.fillWidth: true; spacing: Theme.gap
    UiNotice { active: panel.visible; text: "Surface preview · " + panel.preview.state }
    UiNotice { active: panel.visible; text: panel.preview.error || ""; error: true }
    RowLayout {
        UiButton { objectName:"surfacePreviewAccept"; text:"Accept"; enabled:panel.preview.state==="ready"; onClicked:{ const key=App.runtime.run("surface.preview.accept",{token:panel.preview.token}); if(key) { App.authoring.setEditing(false); App.selection.select(key); } } }
        UiButton { objectName:"surfacePreviewCancel"; text:"Cancel"; onClicked:App.runtime.run("surface.preview.cancel",{}) }
    }
}
