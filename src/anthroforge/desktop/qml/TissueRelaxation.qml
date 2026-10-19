import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiSection {
    id: panel
    required property var item
    property bool supported: true
    readonly property var settings: item.relaxation || ({})
    readonly property bool active: supported && settings.mode !== "NONE"
    title: "Relaxation"; expanded: false
    hint: "Geometric applies the source's sag model. Static PBD solves shape and volume constraints. Neither is animation or physical contact."
    function change(key,value) { const changes={}; changes[key]=value; workspace.run("tissue.relaxation",{target:item.id,changes:changes}); }
    UiCombo { objectName: "tissueRelaxationMode"; Layout.fillWidth: true; model: panel.supported ? ["NONE","GEOMETRIC","STATIC_PBD"] : ["NONE"]; currentIndex: Math.max(0,model.indexOf(panel.settings.mode)); onActivated: panel.change("mode",currentText) }
    Label { visible: !panel.supported; text: "Muscle inflation uses height smoothing."; color: Theme.muted; wrapMode: Text.WordWrap; Layout.fillWidth: true }
    ColumnLayout {
        visible: panel.active; Layout.fillWidth: true; spacing: Theme.gap
        NumericSetting { label: "Sagginess"; value: panel.settings.sagginess || 0; onEdited: value => panel.change("sagginess",value) }
        NumericSetting { label: "Sag limit · 0 = unlimited"; length: true; value: panel.settings.sag_limit || 0; onEdited: value => panel.change("sag_limit",value) }
        Repeater {
            model: ["X","Y","Z"]
            NumericSetting { required property string modelData; required property int index; label: "Gravity " + modelData; value: panel.settings.gravity?.[index] || 0; onEdited: value => { let vector=Array.from(panel.settings.gravity); vector[index]=value; panel.change("gravity",vector); } }
        }
        NumericSetting { label: "Shape retention"; value: panel.settings.shape_retention || 0; onEdited: value => panel.change("shape_retention",value) }
        NumericSetting { visible: panel.settings.mode === "STATIC_PBD"; label: "Volume retention"; value: panel.settings.volume_retention || 0; onEdited: value => panel.change("volume_retention",value) }
        NumericSetting { visible: panel.settings.mode === "STATIC_PBD"; label: "Surface slack"; value: panel.settings.slack || 0; onEdited: value => panel.change("slack",value) }
        NumericSetting { label: "Iterations"; decimals: 0; value: panel.settings.iterations || 24; onEdited: value => panel.change("iterations",Math.round(value)) }
        NumericSetting { visible: panel.settings.mode === "STATIC_PBD"; label: "Constraint passes"; decimals: 0; value: panel.settings.constraint_passes || 2; onEdited: value => panel.change("constraint_passes",Math.round(value)) }
        NumericSetting { visible: panel.settings.mode === "STATIC_PBD"; label: "Convergence tolerance"; decimals: 7; value: panel.settings.tolerance || 0.00001; onEdited: value => panel.change("tolerance",value) }
    }
    Label {
        objectName: "tissueConvergence"; Layout.fillWidth: true; wrapMode: Text.WordWrap
        readonly property var diagnostic: panel.item.diagnostics?.find(d=>d.stage==="intrinsic")
        visible: !!diagnostic && diagnostic.status !== "NOT_APPLICABLE"
        text: diagnostic ? diagnostic.status.split("_").join(" ") + " · " + diagnostic.iterations + " iterations" : ""
        color: diagnostic?.status === "ITERATION_LIMIT" ? Theme.accent : Theme.muted
    }
}
