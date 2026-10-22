import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: editor
    required property var adapter
    property var details: adapter.details
    property string purpose: ""
    property string inputFormula: ""
    property string targetFormula: ""
    spacing: Theme.inset
    RowLayout {
        Layout.fillWidth: true
        UiButton { text: "‹"; hint: "Back to shortcuts"; onClicked: { editor.purpose=""; editor.adapter.select(""); } }
        UiField { text: editor.details.label || ""; placeholderText: "Shortcut label"; Layout.fillWidth: true; onEditingFinished: editor.adapter.configure("label",text) }
    }
    RowLayout {
        visible: editor.details.kind === "DRIVER"; Layout.fillWidth: true
        UiCombo {
            model: ["REAL","INTEGER"]; Layout.fillWidth: true
            currentIndex: model.indexOf(editor.details.numeric_type)
            hint: "Virtual input numerical type"
            onActivated: editor.adapter.configure("numeric_type",currentText)
        }
        UiCombo {
            model: ["SCALAR","LENGTH","ANGLE"]; Layout.fillWidth: true
            currentIndex: model.indexOf(editor.details.dimension)
            hint: "Canonical quantity: dimensionless, metres, or radians"
            onActivated: editor.adapter.configure("dimension",currentText)
        }
    }
    RowLayout {
        visible: editor.details.kind === "DRIVER"; Layout.fillWidth: true
        Label { text: "Value"; color: Theme.text }
        UiNumberField {
            Layout.fillWidth: true; value: editor.details.value || 0
            decimals: editor.details.numeric_type === "INTEGER" ? 0 : 4
            onEdited: value => editor.adapter.setValue(value)
        }
    }
    RowLayout {
        visible: editor.details.kind === "DRIVER"; Layout.fillWidth: true
        Label { text: "Formulas"; color: Theme.text; Layout.fillWidth: true }
        UiButton { text: "Add target"; onClicked: { editor.targetFormula=""; editor.purpose="TARGET"; editor.adapter.discover("","TARGET"); } }
    }
    ShortcutPolicies { Layout.fillWidth: true; adapter: editor.adapter.policies }
    UiButton { visible: editor.details.kind === "DRIVER"; text: "Delete driver"; hint: "Remove this driver and its formulas; retain current target values"; onClicked: editor.adapter.removeDriver() }
    ColumnLayout {
        visible: !!editor.purpose; Layout.fillWidth: true
        RowLayout {
            UiField { id: filter; Layout.fillWidth: true; placeholderText: "Search objects and properties"; onTextChanged: if(editor.purpose) editor.adapter.discover(text,editor.purpose) }
            UiButton { text: "×"; hint: "Close property picker"; onClicked: editor.purpose="" }
        }
        UiField { id: alias; visible: editor.purpose==="INPUT"; Layout.fillWidth: true; placeholderText: "Input name used in expression"; text: "input" }
        ListView {
            objectName: "formulaPropertyPicker"; Layout.fillWidth: true; Layout.preferredHeight: 170
            model: editor.adapter.targets; clip: true; ScrollBar.vertical: ScrollBar {}
            delegate: ItemDelegate {
                required property string label
                required property var reference
                required property string driver
                width: ListView.view.width; height: Math.max(32,choice.implicitHeight+10)
                contentItem: Label { id: choice; text: label; color: Theme.text; wrapMode: Text.Wrap; font.pixelSize: 11 }
                background: Rectangle { color: parent.hovered ? Theme.hover : "transparent" }
                onClicked: {
                    if(editor.purpose==="TARGET" && editor.targetFormula) editor.adapter.updateFormula(editor.targetFormula,{target:reference});
                    else if(editor.purpose==="TARGET") editor.adapter.addFormula(reference);
                    else editor.adapter.addInput(editor.inputFormula,alias.text,reference,driver);
                    editor.purpose="";
                }
            }
        }
    }
    ListView {
        objectName: "drivingFormulaList"; Layout.fillWidth: true; Layout.fillHeight: true
        visible: editor.details.kind === "DRIVER"; model: editor.adapter.formulas
        clip: true; spacing: Theme.inset; ScrollBar.vertical: ScrollBar {}
        delegate: ColumnLayout {
            id: formula
            required property string formulaKey
            required property string label
            required property string expression
            required property var inputs
            required property bool active
            required property string status
            required property string error
            width: ListView.view.width; spacing: 4
            RowLayout {
                Layout.fillWidth: true
                UiCheck { checked: formula.active; onClicked: editor.adapter.updateFormula(formula.formulaKey,{enabled:checked}) }
                Label {
                    text: formula.label; color: Theme.text; wrapMode: Text.Wrap; Layout.fillWidth: true; font.pixelSize: 11
                    TapHandler { onTapped: { editor.targetFormula=formula.formulaKey; editor.purpose="TARGET"; editor.adapter.discover("","TARGET"); } }
                    HoverHandler { id: targetHover }
                    ToolTip.visible: targetHover.hovered; ToolTip.text: "Choose a different target property"
                }
                UiButton { text: "×"; hint: "Remove formula; keep current value"; onClicked: editor.adapter.removeFormula(formula.formulaKey) }
            }
            RowLayout {
                Layout.fillWidth: true
                UiField { Layout.fillWidth: true; text: formula.expression; placeholderText: "value * 2"; onEditingFinished: editor.adapter.updateFormula(formula.formulaKey,{expression:text}) }
                UiButton { text: formula.status === "failed" ? "!" : formula.status === "pending" ? "◷" : "✓"; hint: formula.error || formula.status; flatStyle: true; Layout.preferredWidth: 30 }
            }
            RowLayout {
                Layout.fillWidth: true
                Label { text: "value = this driver's input"; color: Theme.muted; font.pixelSize: 10; Layout.fillWidth: true; wrapMode: Text.Wrap }
                UiButton { text: "+ Input"; onClicked: { editor.inputFormula=formula.formulaKey; editor.purpose="INPUT"; editor.adapter.discover("","INPUT"); } }
            }
            ListView {
                visible: count>0; Layout.fillWidth: true; Layout.preferredHeight: Math.min(120,count*30)
                model: formula.inputs; clip: true; ScrollBar.vertical: ScrollBar {}
                delegate: RowLayout {
                    required property var modelData
                    width: ListView.view.width; height: 30
                    Label { text: modelData.name; color: Theme.text; Layout.fillWidth: true }
                    UiButton { text: "×"; hint: "Remove input"; onClicked: editor.adapter.removeInput(formula.formulaKey,modelData.name) }
                }
            }
        }
    }
}
