import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

UiButton {
    id: button
    objectName: "skinExport"
    text: "Export skin…"
    Layout.fillWidth: true
    property var panel: workspace.skinPanel
    property string destination: ""
    enabled: panel.readiness.export.available && !panel.exporter.busy
    hint: panel.readiness.export.reason || "Export final skin as OBJ, in metres."
    onClicked: file.open()
    FileDialog {
        id: file; title: "Export skin"; fileMode: FileDialog.SaveFile
        defaultSuffix: "obj"; nameFilters: ["Wavefront OBJ (*.obj)"]
        onAccepted: {
            button.destination=selectedFile.toString();
            if(button.panel.readiness.export.warnings.length || workspace.state.blocked) policy.open();
            else button.panel.exporter.start(button.destination,"accepted");
        }
    }
    UiDialog {
        id: policy; parent: Overlay.overlay; anchors.centerIn: parent
        width: Math.min(460,parent ? parent.width-32 : 460); modal: true
        title: "Export skin with pending changes"
        standardButtons: Dialog.Cancel
        contentItem: ColumnLayout {
            spacing: Theme.gap
            Label { text: "Export the accepted skin, or calculate skin from the current project before exporting."; color: Theme.text; wrapMode: Text.Wrap; Layout.fillWidth: true }
            UiButton { text: "Export last accepted"; Layout.fillWidth: true; onClicked: { button.panel.exporter.start(button.destination,"accepted"); policy.close(); } }
            UiButton { text: "Update / rebuild and export"; Layout.fillWidth: true; onClicked: { button.panel.exporter.start(button.destination,"update"); policy.close(); } }
        }
    }
}
