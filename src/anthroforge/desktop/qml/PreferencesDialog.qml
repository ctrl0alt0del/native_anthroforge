import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiDialog {
    id: dialog
    objectName: "preferencesDialog"
    title: "Preferences"
    modal: true; anchors.centerIn: parent
    width: Math.min(620, parent.width-48)
    height: Math.min(implicitHeight, parent.height-48)
    standardButtons: Dialog.Close
    onAboutToShow: preferences.refresh()
    contentItem: UiScrollView {
        id: scroller
        implicitHeight: settings.implicitHeight
        contentWidth: availableWidth; clip: true
    ColumnLayout {
        id: settings
        width: scroller.availableWidth; spacing: Theme.gap
        Label { text: "PROJECTS"; color: Theme.muted; font.pixelSize: 11 }
        UiCheck { objectName:"autosaveEnabled"; text:"Autosave recovery copies"; checked:preferences.state.autosave_enabled; onClicked:preferences.setAutosaveEnabled(checked) }
        NumericSetting { objectName:"autosaveMinutes"; label:"Interval · minutes"; decimals:0; minimum:1; maximum:1440; live:false; enabled:preferences.state.autosave_enabled; value:preferences.state.autosave_minutes; onEdited:value=>preferences.setAutosaveMinutes(value) }
        Label { text:"Keep the latest three copies per project. Active calculations use the latest committed revision."; color:Theme.muted; Layout.fillWidth:true; wrapMode:Text.Wrap }
        RowLayout {
            Layout.fillWidth:true
            UiButton { objectName:"preferencesRecover"; text:"Recover autosave…"; onClicked:{ dialog.close(); workspace.projectLibrary.showRecovery(); } }
            UiButton { objectName:"preferencesAutosaveFolder"; text:"Open autosave folder"; hint:"Browse the recovery copies saved on this computer."; onClicked:workspace.projectLibrary.recoveryBrowser.showFolder() }
        }
        UiButton {
            objectName:"preferencesFileAssociation"; text:"Set file association…"
            enabled:!systemIntegration.associationUnavailable
            hint:systemIntegration.associationUnavailable || "Open .anthroforge projects from File Explorer.\nChoose AnthroForge in Windows Default Apps."
            onClicked:systemIntegration.setupAssociation()
        }
        Label { text: "COMPUTATION"; color: Theme.muted; font.pixelSize: 11 }
        RowLayout {
            Layout.fillWidth: true; spacing: Theme.gap
            Label { text: "ROUTED solver"; color: Theme.text; Layout.fillWidth: true }
            UiHelp {
                explanation: "Choose the solver that routes curves around obstacles.\nCustom is the default. PIQP can be faster for dense routes with many contacts; neither is faster for every curve."
            }
            UiCombo {
                objectName: "routingBackend"; Layout.preferredWidth: 200
                model: ["Custom", "PIQP"]
                currentIndex: preferences.state.routing_backend === "PIQP" ? 1 : 0
                onActivated: preferences.setBackend(currentIndex === 1 ? "PIQP" : "CUSTOM")
                hint: "Numerical solver used to route curves and fibers around obstacles"
            }
        }
        Label {
            Layout.fillWidth: true; wrapMode: Text.WordWrap; color: Theme.muted
            text: "Used on the next calculation. Use Recalculate to update current results."
        }
        RowLayout {
            Layout.fillWidth: true; spacing: Theme.gap
            Label { text: "Fiber propagation"; color: Theme.text; Layout.fillWidth: true }
            UiHelp {
                explanation: "Choose how fibers change shape when their supports move.\nSmooth Shape Preservation spreads motion while retaining the curve's shape and attachment points. Local Surface Following deforms the curve separately near each support. Neither guarantees obstacle clearance; Routed is a separate path engine."
            }
            UiCombo {
                objectName: "fiberPropagation"; Layout.preferredWidth: 260
                model: ["Smooth Shape Preservation", "Local Surface Following"]
                currentIndex: preferences.state.fiber_propagation === "LOCAL_SURFACE" ? 1 : 0
                onActivated: preferences.setFiberPropagation(currentIndex === 1 ? "LOCAL_SURFACE" : "SMOOTH_SHAPE")
                hint: "Applies to future calculations; current results stay unchanged"
            }
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
        Label { text: "Preferences apply to all projects on this computer."; color: Theme.muted; font.pixelSize: 11; Layout.fillWidth:true; wrapMode:Text.Wrap }
        Label {
            objectName: "preferencesError"; Layout.fillWidth: true; Layout.preferredHeight: 50
            wrapMode: Text.WordWrap; color: Theme.danger; text: preferences.state.error
        }
    }
    }
}
