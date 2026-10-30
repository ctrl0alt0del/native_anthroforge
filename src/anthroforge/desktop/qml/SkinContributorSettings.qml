import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    required property var contributor
    readonly property var settings: contributor.settings || ({})
    readonly property var effective: contributor.effective || ({})
    visible: !!contributor.owner
    Layout.fillWidth: true
    spacing: Theme.gap
    function change(key, value) {
        const values = {}; values[key] = value;
        App.runtime.run("skin.contributor.configure", {owner:contributor.owner, values:values});
    }
    Label { text: (panel.contributor.fiber ? "Topology guide: " : "Selected source: ") + (panel.contributor.name || ""); color:Theme.text; font.bold:true; Layout.fillWidth:true; wrapMode:Text.Wrap }
    ColumnLayout {
        enabled: !!panel.contributor.editable
        Layout.fillWidth:true
        Label { text:"Gap settings"; color:Theme.muted; visible:!panel.contributor.fiber }
        UiCombo {
            objectName:"skinSourceGapMode"; Layout.fillWidth:true
            visible:!panel.contributor.fiber
            model:["Use document settings", "Override for this source"]
            currentIndex:panel.settings.gap_mode === "OVERRIDE" ? 1 : 0
            onActivated:panel.change("gap_mode", currentIndex ? "OVERRIDE" : "INHERIT")
        }
        NumericSetting {
            objectName:"skinSourceGapLimit"
            visible:!panel.contributor.fiber
            label:"Maximum gap to close"; minimum:0; maximum:100
            enabled:panel.settings.gap_mode === "OVERRIDE"
            value:100*(panel.effective.gap_limit_ratio || 0)
            hint:"Percent of model longest axis"
            onEdited:value=>panel.change("gap_limit_ratio", value/100)
        }
        NumericSetting {
            objectName:"skinSourceGapStrength"
            visible:!panel.contributor.fiber
            label:"Gap filling strength"; minimum:0; maximum:100
            enabled:panel.settings.gap_mode === "OVERRIDE"
            value:100*(panel.effective.gap_strength || 0)
            hint:"Percent of permitted gap filling"
            onEdited:value=>panel.change("gap_strength", value/100)
        }
        UiCheck {
            objectName:"skinFiberFlow"
            visible:!!panel.contributor.flow_available
            text:"Use as topology FLOW guide"; checked:!!panel.settings.flow
            onToggled:panel.change("flow", checked)
        }
        ColumnLayout {
            visible:!!panel.contributor.scp; Layout.fillWidth:true
            Label { text:"Topology density"; color:Theme.muted }
            UiCombo {
                objectName:"skinSourceDensityMode"; Layout.fillWidth:true
                model:["Use parent budget", "Set subtree budget"]
                currentIndex:panel.settings.density_mode === "SUBTREE_BUDGET" ? 1 : 0
                onActivated:panel.change("density_mode", currentIndex ? "SUBTREE_BUDGET" : "INHERIT")
            }
            NumericSetting {
                label:"Subtree target quads"; minimum:100; maximum:500000; decimals:0
                enabled:panel.settings.density_mode === "SUBTREE_BUDGET"
                value:panel.settings.target_quads || 1000
                onEdited:value=>panel.change("target_quads", Math.round(value))
            }
            Label {
                visible:!!(panel.contributor.budget_errors || []).length
                text:(panel.contributor.budget_errors || []).join("\n")
                color:Theme.muted; Layout.fillWidth:true; wrapMode:Text.Wrap
            }
        }
        ColumnLayout {
            visible:!!panel.contributor.scp; Layout.fillWidth:true
            Label { text:"Collagen"; color:Theme.muted }
            UiCombo {
                objectName:"skinSourceCollagenMode"; Layout.fillWidth:true
                model:["Automatic", "Uniform", "Painted"]
                currentIndex:Math.max(0,["AUTO","UNIFORM","PAINTED"].indexOf(panel.settings.collagen_mode))
                onActivated:panel.change("collagen_mode",["AUTO","UNIFORM","PAINTED"][currentIndex])
            }
            NumericSetting {
                objectName:"skinSourceCollagen"; minimum:0; maximum:1
                label:panel.settings.collagen_mode === "AUTO" ? "Automatic collagen" : "Default collagen"
                enabled:panel.settings.collagen_mode !== "AUTO"
                value:panel.effective.collagen ?? 1
                hint:"0 keeps skin close to bone; 1 allows the full collagen layer."
                onEdited:value=>panel.change("collagen",value)
            }
            TissuePaintingSettings { collagen:true; enabled:!!panel.contributor.surface }
            RowLayout {
                Layout.fillWidth:true; enabled:!!panel.contributor.surface
                UiButton { objectName:"skinCollagenFill"; text:"Fill weights"; Layout.fillWidth:true; onClicked:App.runtime.run("skin.collagen.fill",{owner:panel.contributor.owner}) }
                UiButton { objectName:"skinCollagenClear"; text:"Clear weights"; Layout.fillWidth:true; onClicked:App.runtime.run("skin.collagen.clear",{owner:panel.contributor.owner}) }
            }
        }
    }
    Label { visible:!!panel.contributor.reason; text:panel.contributor.reason || ""; color:Theme.muted; Layout.fillWidth:true; wrapMode:Text.Wrap }
}
