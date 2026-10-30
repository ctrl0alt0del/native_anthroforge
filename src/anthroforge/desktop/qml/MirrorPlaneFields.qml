import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    property var definition: ({axis:"X",shift:0,rule:""})
    readonly property var rules: { const revision=App.runtime.state.revision; return App.mirrors.mirrorPlanes(); }
    readonly property var active: rules.find(r=>r.target===definition.rule) || definition
    signal edited(var value)
    Layout.fillWidth: true; spacing: Theme.gap
    UiCombo {
        objectName: "symmetryPlaneSource"; Layout.fillWidth: true; textRole: "name"
        model: [{target:"",name:"Document plane"}].concat(panel.rules)
        currentIndex: Math.max(0,model.findIndex(r=>r.target===(panel.definition.rule || "")))
        hint: "Use a document-axis plane or follow an existing Mirror Children rule"
        onActivated: panel.edited({rule:model[currentIndex].target,axis:panel.active.axis || "X",shift:panel.active.shift || 0})
    }
    RowLayout {
        enabled: !panel.definition.rule; Layout.fillWidth: true
        UiCombo {
            objectName: "symmetryPlaneAxis"; model: ["X","Y","Z"]; Layout.fillWidth: true
            currentIndex: Math.max(0,model.indexOf(panel.active.axis || "X"))
            onActivated: panel.edited({rule:"",axis:currentText,shift:panel.active.shift || 0})
        }
        UiNumberField {
            objectName: "symmetryPlaneShift"; Layout.fillWidth: true
            value: (panel.active.shift || 0)/App.runtime.state.unit_factor
            step: .001/App.runtime.state.unit_factor; Accessible.name: "Symmetry plane shift"
            onEdited: number=>panel.edited({rule:"",axis:panel.active.axis || "X",shift:number*App.runtime.state.unit_factor})
        }
    }
}
