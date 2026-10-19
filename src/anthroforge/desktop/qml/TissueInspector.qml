import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    readonly property var selected: workspace.selectedData
    readonly property var item: selected.tissue_settings || ({})
    readonly property var part: item.parts?.[0] || ({})
    readonly property var inflation: part.a?.inflation || ({})
    readonly property bool muscleMode: ["DISTRIBUTED","CTRL_POINT","SECTION_PROFILE"].includes(inflation.mode)
    Layout.fillWidth: true; spacing: Theme.gap
    function configure(key,value) { const changes={}; changes[key]=value; workspace.run("tissue.configure",{target:selected.id,changes:changes}); }
    function inflate(key,value) { const changes={}; changes[key]=value; workspace.run("tissue.inflation",{target:selected.id,changes:changes}); }
    UiField {
        id: nameField; objectName: "tissueName"; Layout.fillWidth: true; Accessible.name: "Tissue name"
        Binding { target: nameField; property: "text"; when: !nameField.activeFocus; value: panel.selected.name || "" }
        onEditingFinished: if(panel.selected.is_tissue && text !== panel.selected.name) workspace.run("object.rename",{target:panel.selected.id,name:text})
    }
    UiButton { text: "Edit construction source"; glyph: "curve-points"; Layout.fillWidth: true; onClicked: workspace.select(panel.item.source) }
    UiSection {
        title: "Inflation"
        UiCheck { text: "Enabled"; checked: panel.inflation.enabled ?? true; onClicked: panel.inflate("enabled",checked) }
        UiCombo { objectName: "tissueInflationMode"; Layout.fillWidth: true; model: panel.selected.tissue_modes || []; currentIndex: model.indexOf(panel.inflation.mode); onActivated: panel.inflate("mode",currentText) }
        NumericSetting { label: "Amount"; length: true; value: panel.inflation.amount || 0; onEdited: value => panel.inflate("amount",value) }
        NumericSetting { visible: panel.muscleMode; label: "Boundary band · samples"; value: panel.inflation.boundary_band || 0; onEdited: value => panel.inflate("boundary_band",value) }
        NumericSetting { visible: panel.muscleMode; label: "Boundary attenuation"; value: panel.inflation.boundary_strength || 0; onEdited: value => panel.inflate("boundary_strength",value) }
        NumericSetting { visible: panel.muscleMode; label: "Longitudinal taper"; value: panel.inflation.length_taper || 0; onEdited: value => panel.inflate("length_taper",value) }
        NumericSetting { visible: panel.inflation.mode === "NORMAL"; label: "Minimum thickness"; length: true; value: panel.inflation.minimum || 0; onEdited: value => panel.inflate("minimum",value) }
        NumericSetting { visible: ["NORMAL","PROFILE"].includes(panel.inflation.mode); label: "Profile power"; value: panel.inflation.power || 1; onEdited: value => panel.inflate("power",value) }
        NumericSetting { visible: panel.inflation.mode === "PROFILE"; label: "Half-width"; length: true; value: panel.inflation.width || 0; onEdited: value => panel.inflate("width",value) }
        NumericSetting { visible: panel.inflation.mode === "PROFILE"; label: "Profile segments"; decimals: 0; value: panel.inflation.segments || 11; onEdited: value => panel.inflate("segments",Math.round(value)) }
        NumericSetting { visible: panel.inflation.mode === "PROFILE"; label: "Endpoint taper"; value: panel.inflation.endpoint_taper || 0; onEdited: value => panel.inflate("endpoint_taper",value) }
        Repeater {
            model: panel.inflation.mode === "RADIAL" ? ["X","Y","Z"] : []
            NumericSetting { required property string modelData; required property int index; label: "Scale " + modelData; value: panel.inflation.scale?.[index] || 1; onEdited: value => { let scale=Array.from(panel.inflation.scale); scale[index]=value; panel.inflate("scale",scale); } }
        }
        UiCheck { visible: panel.selected.tissue_domain !== "POINT"; text: "Reverse side"; checked: panel.item.reverse || false; onClicked: panel.configure("reverse",checked) }
    }
    TissueRelaxation { item: panel.item; supported: !panel.muscleMode }
    TissueRegions { item: panel.item; masks: panel.selected.tissue_masks || [] }
    UiSection {
        title: "Evaluation"
        NumericSetting { label: "Material resolution"; decimals: 0; value: panel.item.resolution || 24; onEdited: value => panel.configure("resolution",Math.round(value)) }
        UiCheck { visible: panel.selected.tissue_domain === "SURFACE"; text: "Automatic stacking"; checked: panel.item.stacking || false; onClicked: panel.configure("stacking",checked) }
        UiCombo { Layout.fillWidth: true; model: ["INHERIT","LIVE","ON_RELEASE","MANUAL"]; currentIndex: Math.max(0,model.indexOf(panel.item.update_mode)); onActivated: workspace.run("update_mode",{entity:panel.selected.id,mode:currentText}) }
        UiButton { text: "Evaluate tissue"; Layout.fillWidth: true; onClicked: workspace.run("evaluate",{entities:[panel.selected.id]}) }
    }
}
