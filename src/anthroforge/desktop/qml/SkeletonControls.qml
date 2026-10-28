import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    required property var service
    property var selected: ({})
    property var choices: []
    UiField { id: search; Layout.fillWidth: true; placeholderText: "Search shortcuts and formulas" }
    ListView {
        Layout.fillWidth: true; Layout.fillHeight: true; clip: true; reuseItems: true
        model: (panel.service.state.controls || []).filter(r=>r.name.toLowerCase().includes(search.text.toLowerCase()))
        ScrollBar.vertical: ScrollBar {}
        delegate: UiButton {
            required property var modelData; width: ListView.view.width-14; alignLeft: true
            text: modelData.name; checked: panel.selected === modelData
            hint: modelData.owner+"\n"+modelData.property.path.join(" / ")
            onClicked: { panel.selected=modelData; panel.choices=[]; }
        }
    }
    Label { Layout.fillWidth: true; text: panel.selected.name || "Choose a control"; color: Theme.text; wrapMode: Text.Wrap }
    UiSearchChoice {
        Layout.fillWidth: true; text: "Map to property on…"; choices: (panel.service.state.required || []).concat(panel.service.state.parents || []).map(r=>({id:r.target || r.id,name:r.name}))
        enabled: !!panel.selected.key
        onChosen: row=>{ panel.choices=panel.service.propertyChoices(panel.selected.key,row.id); }
    }
    UiSearchChoice {
        Layout.fillWidth: true; text: "Choose compatible property"; choices: panel.choices; enabled: choices.length>0
        onChosen: row=>panel.service.decision("property_mappings",panel.selected.key,row.property)
    }
    UiCheck {
        text: panel.selected.kind === "shortcut" ? "Remove shortcut" : "Disable formula"
        enabled: !!panel.selected.key
        checked: (panel.service.state.options[panel.selected.kind === "shortcut" ? "remove_shortcuts" : "disable_formulas"] || []).includes(panel.selected.control)
        onClicked: panel.service.decision(panel.selected.kind === "shortcut" ? "remove_shortcuts" : "disable_formulas",panel.selected.control,checked)
    }
}
