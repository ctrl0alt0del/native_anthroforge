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
        UiButton { objectName:"skinBuildEnvelope"; text:"Build envelope"; Layout.fillWidth:true; onClicked:workspace.run("skin.envelope.build",{}) }
        UiCombo {
            objectName:"skinDisplay"; Layout.fillWidth:true; textRole:"label"; valueRole:"id"
            model:[{id:"AUTO",label:"Show latest skin"},{id:"ENVELOPE",label:"Show envelope"},{id:"TOPOLOGY",label:"Show topology"},{id:"FINAL",label:"Show final skin"},{id:"NONE",label:"Hide skin"}]
            currentIndex:indexOfValue(pane.state.display || "AUTO")
            onActivated:workspace.run("workspace.update",{skin_display:currentValue})
        }
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
        SkinTopologySettings { settings:pane.state.topology_settings; onEdited:(key,value)=>pane.change("topology_settings",key,value) }
        SkinDeformationSettings { settings:pane.state.deformation_settings; onEdited:(key,value)=>pane.change("deformation_settings",key,value) }
    }
}
