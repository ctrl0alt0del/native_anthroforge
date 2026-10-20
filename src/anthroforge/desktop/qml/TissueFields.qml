import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiSection {
    id: panel
    required property var item
    property string focused: ""
    readonly property var chosen: item.fields?.find(f=>f.name===focused)
    readonly property bool editing: authoring.state.category==="TISSUE_FIELD" && authoring.state.editing
    readonly property var selection: authoring.componentRows.filter(r=>authoring.state.components.includes(r.key) && r.part==="field" && r.field===panel.focused)
    readonly property real selectedWeight: selection.length ? selection[0].weight : 1
    readonly property bool mixedWeights: selection.some(r=>Math.abs(r.weight-selectedWeight)>1e-9)
    title: "Weight fields"; expanded: false
    hint: "Fields retain material topology. INFLATION controls normal-shell thickness; other names are available as constraint masks."
    UiField { id: name; objectName: "tissueFieldName"; Layout.fillWidth: true; placeholderText: "New field name" }
    RowLayout {
        Layout.fillWidth: true
        UiCombo { id: domain; Layout.fillWidth: true; model: ["BASE","REST"]; hint: "Base samples or inflated-rest vertices" }
        UiButton { objectName: "tissueFieldCreate"; text: "Create"; enabled: !!name.text.trim(); onClicked: { workspace.run("tissue.field.create",{target:panel.item.id,name:name.text.trim(),domain:domain.currentText}); panel.focused=name.text.trim(); } }
    }
    UiField { id: search; Layout.fillWidth: true; placeholderText: "Find a field…"; visible: (panel.item.fields?.length || 0)>0 }
    ListView {
        id: fields; objectName: "tissueFieldList"; Layout.fillWidth: true
        Layout.preferredHeight: Math.min(128,count*32); clip: true; reuseItems: true
        model: (panel.item.fields || []).filter(f=>f.name.toLowerCase().includes(search.text.toLowerCase()))
        ScrollBar.vertical: ScrollBar {}
        delegate: UiButton {
            required property var modelData
            width: fields.width; height: 32; flatStyle: true; alignLeft: true
            text: modelData.name+" · "+modelData.domain; checkable: true; checked: panel.focused===modelData.name
            onClicked: { panel.focused=modelData.name; authoring.editTissueField(modelData.name); }
        }
    }
    ColumnLayout {
        Layout.fillWidth: true; visible: !!panel.chosen; spacing: Theme.gap
        UiButton { objectName: "tissueFieldEdit"; visible: !panel.editing; text: "Edit field"; Layout.fillWidth: true; onClicked: authoring.editTissueField(panel.focused) }
        Label { visible: panel.editing; text: "Ctrl-click to extend selection. Blue = 0, gold = partial, red = 1."; color: Theme.muted; Layout.fillWidth: true; wrapMode: Text.WordWrap }
        RowLayout {
            visible: panel.editing; Layout.fillWidth: true
            UiButton { text: "Select all"; onClicked: authoring.selectAllComponents(true) }
            UiButton { text: "Clear selection"; onClicked: authoring.selectAllComponents(false) }
        }
        NumericSetting { objectName: "tissueFieldWeight"; label: panel.mixedWeights ? "Weight · mixed" : "Weight · 0–1"; mixed: panel.mixedWeights; value: panel.selectedWeight; enabled: panel.editing && panel.selection.length>0; onEdited: value=>authoring.assignTissueWeight(value) }
        UiButton { text: "Finish selection"; visible: panel.editing; Layout.fillWidth: true; onClicked: authoring.setEditing(false) }
        UiButton { objectName: "tissueFieldRemove"; text: "Remove field"; glyph: "delete"; Layout.fillWidth: true; onClicked: workspace.run("tissue.field.remove",{target:panel.item.id,name:panel.focused}) }
    }
}
