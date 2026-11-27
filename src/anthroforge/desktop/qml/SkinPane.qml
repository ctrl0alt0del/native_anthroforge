import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiScrollView {
    id: pane
    readonly property var state: App.skinPanel.state
    readonly property var readiness: App.skinPanel.readiness
    contentWidth: availableWidth
    function change(section,key,value) { const values={}; values[key]=value; App.runtime.run("skin.configure",{section:section,values:values}); }
    function editTopologyBudget() {
        contentItem.contentY = Math.max(0, Math.min(topologySettings.y, contentHeight - availableHeight));
        topologySettings.focusCount();
    }
    ColumnLayout {
        width: pane.availableWidth; spacing: Theme.gap
        Label { text: "Skin"; color: Theme.text; font.pixelSize:16; font.bold:true }
        UiCheck {
            objectName:"skinFinalMode"; text:"Update final skin"; Layout.fillWidth:true
            checked:pane.state.update_mode === "FINAL"
            hint:"Off: update Draft after anatomy edits. On: update the final pipeline."
            onClicked:App.runtime.run("skin.update_mode",{mode:checked ? "FINAL" : "DRAFT"})
        }
        Label {
            objectName:"skinConfigurationState"; Layout.fillWidth:true
            text:pane.state.configuration_state || ""; color:Theme.muted
            elide:Text.ElideRight; maximumLineCount:1
        }
        Label {
            objectName:"skinPipelineState"; Layout.fillWidth:true
            text:pane.state.pipeline?.label || ""; color:Theme.muted
            elide:Text.ElideRight; maximumLineCount:1
            ToolTip.visible:statusHover.hovered && !!pane.state.pipeline?.reason
            ToolTip.text:pane.state.pipeline?.reason || ""
            HoverHandler { id:statusHover }
        }
        UiButton {
            objectName:"skinRetry"; text:"Retry skin update"; Layout.fillWidth:true
            enabled:!!pane.state.pipeline?.can_retry
            onClicked:App.runtime.run("skin.retry",{})
        }
        UiButton { objectName:"skinBuild"; text:"Build Skin"; Layout.fillWidth:true; enabled:pane.readiness.build.available; hint:pane.readiness.build.reason; onClicked:App.runtime.run("skin.build",{}) }
        UiCombo {
            objectName:"skinDisplay"; Layout.fillWidth:true; textRole:"label"; valueRole:"id"
            model:[{id:"AUTO",label:"Follow Draft / Final mode"},{id:"ENVELOPE",label:"Show draft skin"},{id:"TOPOLOGY",label:"Show topology"},{id:"FINAL",label:"Show final skin"},{id:"NONE",label:"Hide skin"}]
            currentIndex:indexOfValue(pane.state.display || "AUTO")
            onActivated:App.runtime.run("workspace.update",{skin_display:currentValue})
        }
        Label { text: "Envelope"; color: Theme.text; font.bold:true; Layout.topMargin:Theme.gap }
        UiCombo {
            objectName:"skinDraftBuilder"; Layout.fillWidth:true; textRole:"label"; valueRole:"id"
            model:[{id:"FIELD",label:"Field envelope"},{id:"AVBD",label:"AVBD (experimental)"}]
            currentIndex:model.findIndex(option => option.id === (pane.state.draft_settings?.backend || "FIELD"))
            hint:"Choose how to build the draft surface for this project."
            onActivated:pane.change("draft_settings","backend",currentValue)
        }
        UiButton { objectName:"skinResetEnvelope"; visible:pane.state.draft_settings?.backend !== "AVBD"; text:"Reset defaults"; hint:"Restore the draft skin offset, collagen and gap settings."; onClicked:App.runtime.run("skin.envelope.reset",{}) }
        UiButton { objectName:"skinBuildEnvelope"; enabled:pane.readiness.envelope.available; hint:pane.readiness.envelope.reason; text:"Rebuild envelope"; Layout.fillWidth:true; onClicked:App.runtime.run("skin.envelope.build",{}) }
        NumericSetting {
            objectName:"skinRootVertices"; visible:pane.state.draft_settings?.backend === "AVBD"
            label:"Initial root vertices"; minimum:4; maximum:500000; decimals:0; step:1; live:false
            value:pane.state.avbd_settings?.root_vertices ?? 402
            hint:"Target for the first envelope only. Later SCP/VCP stages can add vertices and triangles. Rebuild envelope to apply."
            onEdited:value=>pane.change("draft_settings","root_vertices",Math.round(value))
        }
        Repeater {
            model: pane.state.draft_settings?.backend === "AVBD" ? [] : [
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
        SkinContributorSettings { fieldBuilder:pane.state.draft_settings?.backend !== "AVBD"; contributor:pane.state.contributor || ({}) }
        SkinTopologySettings { id:topologySettings; settings:pane.state.topology_settings; onEdited:(key,value)=>pane.change("topology_settings",key,value) }
        SkinTopologyContributorSettings {
            contributor:pane.state.contributor || ({})
            onEditDocumentBudget:pane.editTopologyBudget()
        }
        UiButton { objectName:"skinBuildTopology"; text:"Rebuild topology"; Layout.fillWidth:true; enabled:pane.readiness.topology.available; hint:pane.readiness.topology.reason; onClicked:App.runtime.run("skin.topology.build",{}) }
        SkinDeformationSettings { settings:pane.state.deformation_settings; onEdited:(key,value)=>pane.change("deformation_settings",key,value) }
        UiButton {
            objectName:"skinBuildReference"; text:"Rebuild deformation reference"; Layout.fillWidth:true
            enabled:pane.readiness.reference.available
            hint:pane.readiness.reference.reason || "Initialize skin deformation from the current anatomy and topology."
            onClicked:App.runtime.run("skin.reference.build",{})
        }
        UiButton {
            objectName:"skinUpdate"; text:"Update skin"; Layout.fillWidth:true
            enabled:pane.readiness.update.available; hint:pane.readiness.update.reason
            onClicked:App.runtime.run("skin.evaluate",{})
        }
        SkinFits { adapter: App.skinPanel.fits }
        SkinReports { reports:pane.state.reports || ({}) }
        SkinExport { }
    }
}
