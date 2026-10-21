import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiSection {
    id: panel
    objectName: "tissueInspectionPanel"; title: "Inspect tissue"; expanded: false
    readonly property var tools: workspace.tissueInspection
    readonly property var state: tools.state
    readonly property var options: [{stage:"",label:"Current result"}].concat((state.stages || []).filter(s=>s.available))
    readonly property bool hasMesh: !state.stage || (state.stages || []).some(s=>s.stage===state.stage && s.available && s.kind==="MESH")
    function change(stage,reference,mode) { tools.configure(stage,reference,mode); }
    UiCombo {
        objectName: "tissueInspectStage"; Layout.fillWidth: true; textRole: "label"; model: panel.options
        currentIndex: Math.max(0,model.findIndex(s=>s.stage===panel.state.stage))
        hint: "View an accepted computation stage without changing tissue settings"
        onActivated: panel.change(model[currentIndex].stage,panel.state.reference,panel.state.mode)
    }
    UiCombo {
        objectName: "tissueInspectReference"; Layout.fillWidth: true; textRole: "label"; enabled: !!panel.state.stage
        model: [{stage:"",label:"No comparison"}].concat((panel.state.stages || []).filter(s=>s.available))
        currentIndex: Math.max(0,model.findIndex(s=>s.stage===panel.state.reference))
        onActivated: panel.change(panel.state.stage,model[currentIndex].stage,panel.state.mode)
    }
    UiCombo {
        objectName: "tissueInspectMode"; Layout.fillWidth: true; model: ["Overlay","Displacement"]
        enabled: !!panel.state.stage && !!panel.state.reference
        currentIndex: Math.max(0,model.indexOf(panel.state.mode))
        onActivated: panel.change(panel.state.stage,panel.state.reference,currentText)
    }
    Label { Layout.fillWidth: true; text: panel.state.mode==="Displacement" ? "Blue → yellow → red: increasing displacement" : "Pink: selected stage · green: reference"; color: Theme.muted; wrapMode: Text.WordWrap }
    UiNotice { active: panel.visible; text: panel.state.comparison?.error || ""; error: true }
    UiNotice { active: panel.visible; text: panel.state.pointStatus?.error || ""; error: true }
    UiNotice { active: panel.visible; text: panel.state.comparison?.state==="running" || panel.state.comparison?.state==="queued" ? "Preparing displacement comparison…" : "" }
    UiNotice { active: panel.visible; text: panel.state.pointStatus?.state==="stale" ? "Point evidence is out of date. Pick the current surface again." : "" }
    UiButton { objectName: "tissueExplainPoint"; enabled: panel.hasMesh; text: panel.state.active ? "Finish point inspection" : "Explain a surface point"; checkable: true; checked: panel.state.active; Layout.fillWidth: true; onClicked: panel.tools.explain() }
    UiButton { objectName: "tissueCheckGeometry"; enabled: panel.hasMesh; text: "Check geometry"; Layout.fillWidth: true; hint: "Advisory checks on this stage against itself and other accepted anatomy. Does not modify geometry."; onClicked: panel.tools.check() }
    TissuePointExplanation { report: panel.state.point || ({}) }
    UiSection {
        id: measurements
        title: "Comparison measurements"; expanded: false
        readonly property var report: panel.state.comparison?.report || ({})
        Label { Layout.fillWidth: true; text: measurements.report.maximum===undefined ? "Select two surface stages and Displacement." : "Maximum: "+measurements.report.maximum.toPrecision(5)+" m\nMean: "+measurements.report.mean.toPrecision(5)+" m\nRMS: "+measurements.report.rms.toPrecision(5)+" m"; color: Theme.text; wrapMode: Text.WordWrap }
    }
}
