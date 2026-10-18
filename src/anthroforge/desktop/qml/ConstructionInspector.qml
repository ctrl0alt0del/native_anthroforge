import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    readonly property var selected: workspace.selectedData
    Layout.fillWidth: true; spacing: Theme.gap
    UiField {
        id: nameField; Layout.fillWidth: true; Accessible.name: "Construction object name"
        Binding { target: nameField; property: "text"; when: !nameField.activeFocus; value: panel.selected.name || "" }
        onEditingFinished: if(panel.selected.is_construction && text !== panel.selected.name) workspace.run("object.rename",{target:panel.selected.id,name:text})
    }
    Label { text: panel.selected.kind || ""; color: Theme.muted }
    UiCombo { Layout.fillWidth: true; model: ["INHERIT", "LIVE", "ON_RELEASE", "MANUAL"]; currentIndex: Math.max(0,model.indexOf(panel.selected.update_mode)); onActivated: workspace.run("update_mode",{entity:panel.selected.id,mode:currentText}) }
    UiButton { text: "Delete construction object"; Layout.fillWidth: true; onClicked: workspace.run("object.delete",{target:panel.selected.id}) }
    PrimitiveInspector { visible: panel.selected.kind === "CURVE" || panel.selected.kind === "FIBER" }
}
