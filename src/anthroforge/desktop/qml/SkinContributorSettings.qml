import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    required property var contributor
    readonly property var settings: contributor.settings || ({})
    visible: !!contributor.owner
    Layout.fillWidth: true
    spacing: Theme.gap
    function change(key, value) {
        const values = {}; values[key] = value;
        workspace.run("skin.contributor.configure", {owner:contributor.owner, values:values});
    }
    Label { text: "Selected source: " + (panel.contributor.name || ""); color:Theme.text; font.bold:true; Layout.fillWidth:true; wrapMode:Text.Wrap }
    ColumnLayout {
        enabled: !!panel.contributor.editable
        Layout.fillWidth:true
        Label { text:"Gap settings"; color:Theme.muted }
        UiCombo {
            objectName:"skinSourceGapMode"; Layout.fillWidth:true
            model:["Use document settings", "Override for this source"]
            currentIndex:panel.settings.gap_mode === "OVERRIDE" ? 1 : 0
            onActivated:panel.change("gap_mode", currentIndex ? "OVERRIDE" : "INHERIT")
        }
        NumericSetting {
            label:"Maximum gap to close"; minimum:0; maximum:100
            enabled:panel.settings.gap_mode === "OVERRIDE"
            value:100*(panel.settings.gap_limit_ratio || 0)
            hint:"Percent of model longest axis"
            onEdited:value=>panel.change("gap_limit_ratio", value/100)
        }
        NumericSetting {
            label:"Gap filling strength"; minimum:0; maximum:100
            enabled:panel.settings.gap_mode === "OVERRIDE"
            value:100*(panel.settings.gap_strength || 0)
            hint:"Percent of permitted gap filling"
            onEdited:value=>panel.change("gap_strength", value/100)
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
                objectName:"skinSourceCollagen"; label:"Default collagen"; minimum:0; maximum:1
                value:panel.settings.collagen === undefined ? 1 : panel.settings.collagen
                hint:"0 keeps skin close to bone; 1 allows the full collagen layer."
                onEdited:value=>panel.change("collagen",value)
            }
            TissuePaintingSettings { collagen:true; enabled:!!panel.contributor.surface }
            RowLayout {
                Layout.fillWidth:true; enabled:!!panel.contributor.surface
                UiButton { objectName:"skinCollagenFill"; text:"Fill weights"; Layout.fillWidth:true; onClicked:workspace.run("skin.collagen.fill",{owner:panel.contributor.owner}) }
                UiButton { objectName:"skinCollagenClear"; text:"Clear weights"; Layout.fillWidth:true; onClicked:workspace.run("skin.collagen.clear",{owner:panel.contributor.owner}) }
            }
        }
    }
    Label { visible:!!panel.contributor.reason; text:panel.contributor.reason || ""; color:Theme.muted; Layout.fillWidth:true; wrapMode:Text.Wrap }
}
