import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiScrollView {
    id: pane
    readonly property var state: workspace.skinPanel.state
    readonly property var readiness: workspace.skinPanel.readiness
    contentWidth: availableWidth
    function change(section,key,value) { const values={}; values[key]=value; workspace.run("skin.configure",{section:section,values:values}); }
    ColumnLayout {
        width: pane.availableWidth; spacing: Theme.gap
        Label { text: "Skin"; color: Theme.text; font.pixelSize:16; font.bold:true }
        UiButton { objectName:"skinBuild"; text:"Build Skin"; Layout.fillWidth:true; enabled:pane.readiness.build.available; hint:pane.readiness.build.reason; onClicked:workspace.run("skin.build",{}) }
        UiCombo {
            objectName:"skinDisplay"; Layout.fillWidth:true; textRole:"label"; valueRole:"id"
            model:[{id:"AUTO",label:"Show latest skin"},{id:"ENVELOPE",label:"Show envelope"},{id:"TOPOLOGY",label:"Show topology"},{id:"FINAL",label:"Show final skin"},{id:"NONE",label:"Hide skin"}]
            currentIndex:indexOfValue(pane.state.display || "AUTO")
            onActivated:workspace.run("workspace.update",{skin_display:currentValue})
        }
        Label { text: "Envelope"; color: Theme.text; font.bold:true; Layout.topMargin:Theme.gap }
        UiButton { objectName:"skinResetEnvelope"; text:"Reset defaults"; hint:"Restore the draft skin offset, collagen and gap settings."; onClicked:workspace.run("skin.envelope.reset",{}) }
        UiButton { objectName:"skinBuildEnvelope"; text:"Rebuild envelope"; Layout.fillWidth:true; onClicked:workspace.run("skin.envelope.build",{}) }
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
        SkinContributorSettings { contributor:pane.state.contributor || ({}) }
        SkinTopologySettings { settings:pane.state.topology_settings; onEdited:(key,value)=>pane.change("topology_settings",key,value) }
        UiButton { objectName:"skinBuildTopology"; text:"Rebuild topology"; Layout.fillWidth:true; enabled:pane.readiness.topology.available; hint:pane.readiness.topology.reason; onClicked:workspace.run("skin.topology.build",{}) }
        SkinDeformationSettings { settings:pane.state.deformation_settings; onEdited:(key,value)=>pane.change("deformation_settings",key,value) }
        UiButton {
            objectName:"skinBuildReference"; text:"Rebuild deformation reference"; Layout.fillWidth:true
            enabled:pane.readiness.reference.available
            hint:pane.readiness.reference.reason || "Initialize skin deformation from the current anatomy and topology."
            onClicked:workspace.run("skin.reference.build",{})
        }
        UiButton {
            objectName:"skinUpdate"; text:"Update skin"; Layout.fillWidth:true
            enabled:pane.readiness.update.available; hint:pane.readiness.update.reason
            onClicked:workspace.run("skin.evaluate",{})
        }
        SkinFits { adapter: workspace.skinPanel.fits }
        SkinExport { }
    }
}
