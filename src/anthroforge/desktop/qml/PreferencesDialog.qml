import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiDialog {
    id: dialog
    objectName: "preferencesDialog"
    title: "Preferences"
    modal: true; anchors.centerIn: parent
    width: 480
    standardButtons: Dialog.Close
    onAboutToShow: preferences.refresh()
    ColumnLayout {
        anchors.fill: parent; spacing: Theme.gap
        Label { text: "COMPUTATION"; color: Theme.muted; font.pixelSize: 11 }
        RowLayout {
            Layout.fillWidth: true; spacing: Theme.gap
            Label { text: "ROUTED solver"; color: Theme.text; Layout.fillWidth: true }
            UiHelp {
                explanation: "Custom is the default. PIQP uses a sparse solver and can be faster for densely sampled routes with many contacts. Neither is faster for every curve."
            }
            UiCombo {
                objectName: "routingBackend"; Layout.preferredWidth: 200
                model: ["Custom", "PIQP"]
                currentIndex: preferences.state.routing_backend === "PIQP" ? 1 : 0
                onActivated: preferences.setBackend(currentIndex === 1 ? "PIQP" : "CUSTOM")
                hint: "QP solver used by routed curves and fibers"
            }
        }
        Label {
            Layout.fillWidth: true; wrapMode: Text.WordWrap; color: Theme.muted
            text: "Applies to future calculations. Current results stay unchanged. Use Recalculate to update them."
        }
        Label { text: "CURVE CONVERSION"; color: Theme.muted; font.pixelSize: 11 }
        RowLayout {
            Layout.fillWidth: true; spacing: Theme.gap
            Label { text: "Switch to ROUTED"; color: Theme.text; Layout.fillWidth: true }
            UiHelp {
                explanation: "Endpoints only lets the solver find the path between endpoints. Shared junctions and anatomical binding points are also kept. Closed curves keep all points. Applies only to future engine switches."
            }
            UiCombo {
                objectName: "routingConversionPoints"; Layout.preferredWidth: 200
                model: ["Endpoints only", "All curve points"]
                currentIndex: preferences.state.routing_conversion_points === "ALL_POINTS" ? 1 : 0
                onActivated: preferences.setRoutingConversionPoints(currentIndex === 1 ? "ALL_POINTS" : "ENDPOINTS")
                hint: "Control points retained when switching to the ROUTED engine"
            }
        }
        Label { text: "Saved automatically for all projects on this computer."; color: Theme.muted; font.pixelSize: 11 }
        Label {
            objectName: "preferencesError"; Layout.fillWidth: true; Layout.preferredHeight: 50
            wrapMode: Text.WordWrap; color: Theme.danger; text: preferences.state.error
        }
    }
}
