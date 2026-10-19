import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    readonly property var preview: workspace.surfacePreview
    visible: preview.state!=="idle"
    Layout.fillWidth: true; spacing: Theme.gap
    Label { text: "Surface preview · " + panel.preview.state; color: Theme.accent; Layout.fillWidth: true; wrapMode: Text.WordWrap }
    Label { visible: !!panel.preview.error; text: panel.preview.error || ""; color: Theme.muted; Layout.fillWidth: true; wrapMode: Text.WordWrap }
    RowLayout {
        UiButton { objectName:"surfacePreviewAccept"; text:"Accept"; enabled:panel.preview.state==="ready"; onClicked:{ const key=workspace.run("surface.preview.accept",{token:panel.preview.token}); if(key) { authoring.setEditing(false); workspace.select(key); } } }
        UiButton { objectName:"surfacePreviewCancel"; text:"Cancel"; onClicked:workspace.run("surface.preview.cancel",{}) }
    }
}
