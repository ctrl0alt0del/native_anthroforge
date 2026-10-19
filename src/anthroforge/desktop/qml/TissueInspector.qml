import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    readonly property var selected: workspace.selectedData
    readonly property var item: selected.tissue_settings || ({})
    readonly property var part: item.parts?.[0] || ({})
    readonly property var inflation: part.a?.inflation || ({})
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
        UiCombo { objectName: "tissueInflationMode"; Layout.fillWidth: true; model: ["DISTRIBUTED","CTRL_POINT","SECTION_PROFILE"]; currentIndex: model.indexOf(panel.inflation.mode); onActivated: panel.inflate("mode",currentText) }
        NumericSetting { label: "Amount"; length: true; value: panel.inflation.amount || 0; onEdited: value => panel.inflate("amount",value) }
        NumericSetting { label: "Boundary band · samples"; value: panel.inflation.boundary_band || 0; onEdited: value => panel.inflate("boundary_band",value) }
        NumericSetting { label: "Boundary attenuation"; value: panel.inflation.boundary_strength || 0; onEdited: value => panel.inflate("boundary_strength",value) }
        NumericSetting { label: "Longitudinal taper"; value: panel.inflation.length_taper || 0; onEdited: value => panel.inflate("length_taper",value) }
        UiCheck { text: "Reverse side"; checked: panel.item.reverse || false; onClicked: panel.configure("reverse",checked) }
    }
    UiSection {
        title: "Evaluation"
        NumericSetting { label: "Material resolution"; decimals: 0; value: panel.item.resolution || 24; onEdited: value => panel.configure("resolution",Math.round(value)) }
        UiCheck { text: "Automatic stacking"; checked: panel.item.stacking || false; onClicked: panel.configure("stacking",checked) }
        UiCombo { Layout.fillWidth: true; model: ["INHERIT","LIVE","ON_RELEASE","MANUAL"]; currentIndex: Math.max(0,model.indexOf(panel.item.update_mode)); onActivated: workspace.run("update_mode",{entity:panel.selected.id,mode:currentText}) }
        UiButton { text: "Evaluate tissue"; Layout.fillWidth: true; onClicked: workspace.run("evaluate",{entities:[panel.selected.id]}) }
    }
}
