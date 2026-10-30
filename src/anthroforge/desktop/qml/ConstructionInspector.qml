import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    readonly property var selected: App.selection.selectedData
    readonly property bool dialogVisible: imageInspector.dialogVisible
    readonly property var parents: { const revision=App.runtime.state.revision; const selected=App.selection.selectedId; return App.construction.ordinaryParents(); }
    signal deleteRequested(string entity)
    Layout.fillWidth: true; spacing: Theme.gap
    enabled: !selected.readonly && !App.runtime.state.waiting
    UiField {
        id: nameField; Layout.fillWidth: true; Accessible.name: "Construction object name"
        Binding { target: nameField; property: "text"; when: !nameField.activeFocus; value: panel.selected.name || "" }
        onEditingFinished: if(panel.selected.is_construction && text !== panel.selected.name) App.runtime.run("object.rename",{target:panel.selected.id,name:text})
    }
    PrimitiveInspector { visible: panel.selected.kind === "CURVE" || panel.selected.kind === "FIBER" }
    ImageInspector { id: imageInspector; visible: panel.selected.kind === "IMAGE" }
    SurfaceInspector { visible: ["SURFACE","MEMBRANE"].includes(panel.selected.kind) }
    PointInspector { item: panel.selected; visible: ["POINT","ANCHOR"].includes(panel.selected.kind) }
    TissueCreate { selected: panel.selected; visible: !!panel.selected.tissue_presets?.length }
    FiberCreation { visible: panel.selected.kind==="CURVE"; curve: App.authoring.state.curves?.[0] || ({}) }
    Label { visible: !!panel.selected.users?.length; text: "Used by: "+(panel.selected.users || []).map(u=>u.name).join(", "); color: Theme.muted; Layout.fillWidth: true; wrapMode: Text.WordWrap }
    UiSection { title:"Transform & relationships"; stateKey:"construction/relationships"; expanded:false
    ObjectTransform { selected: panel.selected; visible: panel.selected.kind !== "ANCHOR" }
    UiCombo { Layout.fillWidth: true; model: panel.parents; textRole: "name"; valueRole: "id"; currentIndex: indexOfValue(panel.selected.parent || ""); hint: "Ordinary transform parent · preserves world placement"; onActivated: App.runtime.run("object.reparent",{target:panel.selected.id,parent:currentValue}) }
    UiCombo { enumLabels:true; visible: panel.selected.kind !== "IMAGE"; Layout.fillWidth: true; model: ["INHERIT", "LIVE", "ON_RELEASE", "MANUAL"]; currentIndex: Math.max(0,model.indexOf(panel.selected.update_mode)); onActivated: App.runtime.run("update_mode",{entity:panel.selected.id,mode:currentText}) }
    UiButton { text: "Delete construction object"; Layout.fillWidth: true; onClicked: panel.deleteRequested(panel.selected.id) }

    }
}
