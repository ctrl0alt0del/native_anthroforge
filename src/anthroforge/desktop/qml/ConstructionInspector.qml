import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    readonly property var selected: workspace.selectedData
    readonly property bool dialogVisible: imageInspector.dialogVisible
    readonly property var parents: { const revision=workspace.state.revision; const selected=workspace.selectedId; return workspace.ordinaryParents(); }
    Layout.fillWidth: true; spacing: Theme.gap
    enabled: !selected.readonly && !workspace.state.waiting
    UiField {
        id: nameField; Layout.fillWidth: true; Accessible.name: "Construction object name"
        Binding { target: nameField; property: "text"; when: !nameField.activeFocus; value: panel.selected.name || "" }
        onEditingFinished: if(panel.selected.is_construction && text !== panel.selected.name) workspace.run("object.rename",{target:panel.selected.id,name:text})
    }
    Label { text: panel.selected.kind || ""; color: Theme.muted }
    Label { visible: !!panel.selected.users?.length; text: "Used by: "+(panel.selected.users || []).map(u=>u.name).join(", "); color: Theme.muted; Layout.fillWidth: true; wrapMode: Text.WordWrap }
    ObjectTransform { selected: panel.selected }
    UiCombo { Layout.fillWidth: true; model: panel.parents; textRole: "name"; valueRole: "id"; currentIndex: indexOfValue(panel.selected.parent || ""); hint: "Ordinary transform parent · preserves world placement"; onActivated: workspace.run("object.reparent",{target:panel.selected.id,parent:currentValue}) }
    UiCombo { visible: panel.selected.kind !== "IMAGE"; Layout.fillWidth: true; model: ["INHERIT", "LIVE", "ON_RELEASE", "MANUAL"]; currentIndex: Math.max(0,model.indexOf(panel.selected.update_mode)); onActivated: workspace.run("update_mode",{entity:panel.selected.id,mode:currentText}) }
    UiButton { text: "Delete construction object"; Layout.fillWidth: true; onClicked: workspace.run("object.delete",{target:panel.selected.id}) }
    PrimitiveInspector { visible: panel.selected.kind === "CURVE" || panel.selected.kind === "FIBER" }
    ImageInspector { id: imageInspector; visible: panel.selected.kind === "IMAGE" }
    SurfaceInspector { visible: panel.selected.kind === "SURFACE" }
}
