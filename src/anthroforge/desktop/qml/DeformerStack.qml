import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiSection {
    id: panel
    property var item: ({})
    title: "Deformers"
    RowLayout {
        UiButton { text: "Add Hook"; onClicked: authoring.addDeformer("HOOK"); Layout.fillWidth: true }
        UiButton { text: "Add Lattice"; visible: !panel.item.is_control; onClicked: authoring.addDeformer("LATTICE"); Layout.fillWidth: true }
    }
    Label { text: "Select points in Edit Primitive to bind a Hook to a selection."; color: Theme.muted; wrapMode: Text.WordWrap; Layout.fillWidth: true; font.pixelSize: 11 }
    Repeater {
        model: panel.item.deformers || []
        ColumnLayout {
            id: bindingPanel
            required property var modelData
            readonly property var binding: modelData
            readonly property string controlName: (authoring.state.controls.find(c=>c.id===binding.control) || {}).name || "Missing control"
            Layout.fillWidth: true; spacing: 5
            function set(key,value) { const args={binding:binding.id}; args[key]=value; authoring.edit("deformer.update",args); }
            function reorder(delta) {
                const list=(panel.item.deformers || []).filter(b=>b.target.stage===binding.target.stage && b.target.component===binding.target.component).map(b=>b.id);
                const index=list.indexOf(binding.id), next=index+delta;
                if(next<0 || next>=list.length) return;
                [list[index],list[next]]=[list[next],list[index]];
                authoring.edit("deformer.order",{target:binding.target,bindings:list});
            }
            Rectangle { Layout.fillWidth: true; implicitHeight: 1; color: Theme.border }
            RowLayout {
                UiCheck { text: bindingPanel.binding.kind; checked: bindingPanel.binding.enabled; onClicked: bindingPanel.set("enabled",checked) }
                UiButton { text: bindingPanel.controlName; flatStyle: true; Layout.fillWidth: true; onClicked: workspace.select(bindingPanel.binding.control) }
            }
            Label { text: bindingPanel.binding.target.stage + (bindingPanel.binding.target.component ? " · defining curve/piece" : ""); color: Theme.muted; font.pixelSize: 10 }
            NumericSetting { label: "Strength"; value: bindingPanel.binding.strength; onEdited: value => bindingPanel.set("strength",value) }
            ColumnLayout {
                visible: bindingPanel.binding.kind === "HOOK"; Layout.fillWidth: true
                UiCombo { Layout.fillWidth: true; model: ["NONE","CURVE","SMOOTH","SPHERE","ROOT","SHARP","LINEAR","CONSTANT","INVERSE_SQUARE"]; currentIndex: model.indexOf(bindingPanel.binding.falloff); onActivated: bindingPanel.set("falloff",currentText) }
                NumericSetting { label: "Falloff radius · m"; value: bindingPanel.binding.radius; onEdited: value => bindingPanel.set("radius",value) }
                UiCheck { text: "Uniform falloff"; checked: bindingPanel.binding.uniform; onClicked: bindingPanel.set("uniform",checked) }
                VectorSetting { label: "Falloff center"; values: bindingPanel.binding.center; onEdited: values => authoring.edit("hook.recenter",{binding:bindingPanel.binding.id,center:values}) }
                UiField { visible: bindingPanel.binding.falloff === "CURVE"; Layout.fillWidth: true; placeholderText: "Falloff XY pairs"; text: bindingPanel.binding.custom.join(", "); onEditingFinished: bindingPanel.set("custom",text.split(",").map(Number)) }
                UiField { visible: bindingPanel.binding.falloff === "CURVE"; Layout.fillWidth: true; placeholderText: "AUTO / VECTOR / AUTO_CLAMPED per point"; text: bindingPanel.binding.custom_handles.join(", "); onEditingFinished: bindingPanel.set("custom_handles",text.trim()?text.split(",").map(s=>s.trim().toUpperCase()):[]) }
                UiCheck { visible: bindingPanel.binding.falloff === "CURVE"; text: "Extrapolate falloff ends"; checked: bindingPanel.binding.custom_extrapolate; onClicked: bindingPanel.set("custom_extrapolate",checked) }
                UiField { Layout.fillWidth: true; placeholderText: "Member indices (empty = none)"; text: bindingPanel.binding.indices.join(", "); onEditingFinished: bindingPanel.set("indices",text.trim()?text.split(",").map(Number):[]) }
                RowLayout {
                    UiButton { text: "Assign selected"; onClicked: authoring.members(bindingPanel.binding.id,true) }
                    UiButton { text: "Select members"; onClicked: authoring.members(bindingPanel.binding.id,false) }
                    UiButton { text: "Reset"; onClicked: authoring.edit("hook.reset",{binding:bindingPanel.binding.id}) }
                }
            }
            UiCheck { text: "Invert weights"; checked: bindingPanel.binding.invert; onClicked: bindingPanel.set("invert",checked) }
            RowLayout {
                UiField { id: selectedWeight; text: "1"; placeholderText: "Selected weight"; Layout.fillWidth: true }
                UiButton { text: "Set selected weight"; onClicked: authoring.weights(bindingPanel.binding.id,Number(selectedWeight.text)) }
            }
            UiField { Layout.fillWidth: true; placeholderText: "Influence weights, comma separated"; text: bindingPanel.binding.weights.join(", "); onEditingFinished: bindingPanel.set("weights",text.trim()?text.split(",").map(Number):[]) }
            RowLayout {
                UiButton { text: "Up"; onClicked: bindingPanel.reorder(-1) }
                UiButton { text: "Down"; onClicked: bindingPanel.reorder(1) }
                UiButton { text: "Remove binding"; Layout.fillWidth: true; onClicked: authoring.edit("deformer.remove",{binding:bindingPanel.binding.id}) }
            }
        }
    }
}
