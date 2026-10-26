import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiScrollView {
    id: pane
    readonly property var state: workspace.skinPanel.state
    contentWidth: availableWidth
    function change(section,key,value) { const values={}; values[key]=value; workspace.run("skin.configure",{section:section,values:values}); }
    ColumnLayout {
        width: pane.availableWidth; spacing: Theme.gap
        Label { text: "Skin"; color: Theme.text; font.pixelSize:16; font.bold:true }
        Label { text: "Envelope"; color: Theme.text; font.bold:true; Layout.topMargin:Theme.gap }
        Repeater {
            model: [
                {key:"minimum_offset_ratio",label:"Minimum skin distance",maximum:2},
                {key:"collagen_depth_ratio",label:"Collagen depth",maximum:4},
                {key:"collagen_core_ratio",label:"Collagen core radius",maximum:5},
                {key:"collagen_falloff_ratio",label:"Collagen falloff",maximum:10},
                {key:"gap_limit_ratio",label:"Maximum gap to close",maximum:100},
                {key:"gap_strength",label:"Gap filling strength",maximum:100}
            ]
            NumericSetting {
                required property var modelData
                objectName: "skin_"+modelData.key; label:modelData.label
                minimum:0; maximum:modelData.maximum
                value:100*(pane.state.envelope_settings?.[modelData.key] || 0)
                hint:modelData.key==="gap_strength" ? "Percent of permitted gap filling" : "Percent of model longest axis"
                onEdited: value=>pane.change("envelope_settings",modelData.key,value/100)
            }
        }
        Label { text:"Topology"; color:Theme.text; font.bold:true; Layout.topMargin:Theme.gap }
        UiCombo { objectName:"skinBackend"; Layout.fillWidth:true; enumLabels:true; model:["QUADWILD","INSTANT"]; currentIndex:model.indexOf(pane.state.topology_settings?.backend); onActivated:pane.change("topology_settings","backend",currentText) }
        NumericSetting { objectName:"skinQuadCount"; label:"Target quads"; minimum:1000; maximum:500000; decimals:0; value:pane.state.topology_settings?.target_quads || 8100; onEdited:value=>pane.change("topology_settings","target_quads",value) }
        UiCombo { objectName:"skinRefinement"; Layout.fillWidth:true; enumLabels:true; model:["NONE","MUSCLE_PROXIMITY"]; currentIndex:model.indexOf(pane.state.topology_settings?.refinement); onActivated:pane.change("topology_settings","refinement",currentText) }
        Label { text:"Deformation"; color:Theme.text; font.bold:true; Layout.topMargin:Theme.gap }
        UiCombo { objectName:"skinDeformation"; Layout.fillWidth:true; enumLabels:true; model:["LE","FAST"]; currentIndex:model.indexOf(pane.state.deformation_settings?.method); onActivated:pane.change("deformation_settings","method",currentText) }
    }
}
