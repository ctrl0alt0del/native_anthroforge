import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    readonly property var preview: workspace.surfacePreview
    visible: preview.state!=="idle"
    Layout.fillWidth: true; spacing: Theme.gap
    UiNotice { active: panel.visible; text: "Surface preview · " + panel.preview.state }
    UiNotice { active: panel.visible; text: panel.preview.error || ""; error: true }
    RowLayout {
        UiButton { objectName:"surfacePreviewAccept"; text:"Accept"; enabled:panel.preview.state==="ready"; onClicked:{ const key=workspace.run("surface.preview.accept",{token:panel.preview.token}); if(key) { authoring.setEditing(false); workspace.select(key); } } }
        UiButton { objectName:"surfacePreviewCancel"; text:"Cancel"; onClicked:workspace.run("surface.preview.cancel",{}) }
    }
}
