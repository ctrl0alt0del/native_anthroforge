import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiSection {
    id: panel
    property var item: ({})
    title: "Deformers"
    hint: item.stable_geometry_members === false ? "Edit cage points for local deformation of a Segment Chain." : "Select points in Edit Primitive to bind a Hook to a selection."
    RowLayout {
        UiButton { text: "Add Hook"; onClicked: authoring.addDeformer("HOOK"); Layout.fillWidth: true }
        UiButton { text: "Add Lattice"; visible: !panel.item.is_control; onClicked: authoring.addDeformer("LATTICE"); Layout.fillWidth: true }
    }
    UiSection {
        title: "Add Shrinkwrap"; expanded: false; visible: !panel.item.is_control
        SurfaceSelector {
            onActivated: surface => authoring.edit("shrinkwrap.add", {target:{owner:panel.item.id},surface:{target:surface.id,role:surface.role}})
        }
    }
    RowLayout {
        visible: !panel.item.is_control
        UiButton { text:"Add Subdivision"; onClicked:authoring.edit("modifier.add",{entity:panel.item.id,kind:"SUBDIVISION"}) }
        UiButton { text:"Add Displacement"; onClicked:authoring.edit("modifier.add",{entity:panel.item.id,kind:"DISPLACE"}) }
    }
    Repeater {
        model: panel.item.deformers || []
        ColumnLayout {
            id: bindingPanel
            required property var modelData
            readonly property var binding: modelData
            readonly property string controlName: binding.shrinkwrap ? "Target surface" : (authoring.state.controls.find(c=>c.id===binding.control) || {}).name || "Missing control"
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
                UiButton { visible:!!bindingPanel.binding.control || !!bindingPanel.binding.shrinkwrap; text: bindingPanel.controlName; flatStyle: true; Layout.fillWidth: true; onClicked: workspace.select(bindingPanel.binding.shrinkwrap?.surface.target || bindingPanel.binding.control) }
            }
            Label { text: bindingPanel.binding.target.stage + (bindingPanel.binding.target.component ? " · defining curve/piece" : ""); color: Theme.muted; font.pixelSize: 10 }
            NumericSetting { propertyReference: ({target:panel.item.id,path:["deformers","@"+bindingPanel.binding.id,"strength"]}); visible:bindingPanel.binding.kind!=="SUBDIVISION"; label: "Strength"; value: bindingPanel.binding.strength; onEdited: value => bindingPanel.set("strength",value) }
            ShrinkwrapSettings { binding: bindingPanel.binding; visible: !!bindingPanel.binding.shrinkwrap }
            NumericSetting { propertyReference: ({target:panel.item.id,path:["deformers","@"+bindingPanel.binding.id,"subdivision"]}); visible:bindingPanel.binding.kind==="SUBDIVISION"; label:"Simple subdivision levels"; decimals:0; minimum:0; maximum:5; value:bindingPanel.binding.subdivision || 0; onEdited:value=>authoring.edit("modifier.update",{binding:bindingPanel.binding.id,levels:Math.round(value)}) }
            VectorSetting { propertyReference: ({target:panel.item.id,path:["deformers","@"+bindingPanel.binding.id,"displacement"]}); visible:bindingPanel.binding.kind==="DISPLACE"; length:true; label:"Local displacement"; values:bindingPanel.binding.displacement || [0,0,0]; onEdited:values=>authoring.edit("modifier.update",{binding:bindingPanel.binding.id,offset:values}) }
            ColumnLayout {
                visible: bindingPanel.binding.kind === "HOOK"; Layout.fillWidth: true
                UiCombo { enumLabels:true; Layout.fillWidth: true; model: ["NONE","CURVE","SMOOTH","SPHERE","ROOT","SHARP","LINEAR","CONSTANT","INVERSE_SQUARE"]; currentIndex: model.indexOf(bindingPanel.binding.falloff); onActivated: bindingPanel.set("falloff",currentText) }
                NumericSetting { propertyReference: ({target:panel.item.id,path:["deformers","@"+bindingPanel.binding.id,"radius"]}); length: true; label: "Falloff radius"; value: bindingPanel.binding.radius; onEdited: value => bindingPanel.set("radius",value) }
                UiCheck { text: "Uniform falloff"; checked: bindingPanel.binding.uniform; onClicked: bindingPanel.set("uniform",checked) }
                VectorSetting { propertyReference: ({target:panel.item.id,path:["deformers","@"+bindingPanel.binding.id,"center"]}); length: true; label: "Falloff center"; values: bindingPanel.binding.center; onEdited: values => authoring.edit("hook.recenter",{binding:bindingPanel.binding.id,center:values}) }
                UiField { visible: bindingPanel.binding.falloff === "CURVE"; Layout.fillWidth: true; placeholderText: "Falloff XY pairs"; text: bindingPanel.binding.custom.join(", "); onEditingFinished: bindingPanel.set("custom",text.split(",").map(Number)) }
                UiField { visible: bindingPanel.binding.falloff === "CURVE"; Layout.fillWidth: true; placeholderText: "AUTO / VECTOR / AUTO_CLAMPED per point"; text: bindingPanel.binding.custom_handles.join(", "); onEditingFinished: bindingPanel.set("custom_handles",text.trim()?text.split(",").map(s=>s.trim().toUpperCase()):[]) }
                UiCheck { visible: bindingPanel.binding.falloff === "CURVE"; text: "Extrapolate falloff ends"; checked: bindingPanel.binding.custom_extrapolate; onClicked: bindingPanel.set("custom_extrapolate",checked) }
                UiField { visible:panel.item.stable_geometry_members !== false; Layout.fillWidth: true; placeholderText: "Member indices (empty = none)"; text: bindingPanel.binding.indices.join(", "); onEditingFinished: bindingPanel.set("indices",text.trim()?text.split(",").map(Number):[]) }
                Flow {
                    Layout.fillWidth: true; spacing: 4
                    UiButton { visible:panel.item.stable_geometry_members !== false; text: "Assign selected"; onClicked: authoring.members(bindingPanel.binding.id,true) }
                    UiButton { visible:panel.item.stable_geometry_members !== false; text: "Select members"; onClicked: authoring.members(bindingPanel.binding.id,false) }
                    UiButton { text: "Reset"; onClicked: authoring.edit("hook.reset",{binding:bindingPanel.binding.id}) }
                }
            }
            UiCheck { visible:bindingPanel.binding.kind!=="SUBDIVISION"; text: "Invert weights"; checked: bindingPanel.binding.invert; onClicked: bindingPanel.set("invert",checked) }
            RowLayout {
                visible:bindingPanel.binding.kind!=="SUBDIVISION" && panel.item.stable_geometry_members !== false
                UiNumberField { id: selectedWeight; value: 1; live: false; minimum: 0; maximum: 1; Accessible.name: "Selected weight"; Layout.fillWidth: true; onEdited: number=>value=number }
                UiButton { text: "Set selected weight"; onClicked: authoring.weights(bindingPanel.binding.id,selectedWeight.value) }
            }
            UiField { visible:bindingPanel.binding.kind!=="SUBDIVISION" && panel.item.stable_geometry_members !== false; Layout.fillWidth: true; placeholderText: "Influence weights, comma separated"; text: bindingPanel.binding.weights.join(", "); onEditingFinished: bindingPanel.set("weights",text.trim()?text.split(",").map(Number):[]) }
            RowLayout {
                UiButton { text: "Up"; onClicked: bindingPanel.reorder(-1) }
                UiButton { text: "Down"; onClicked: bindingPanel.reorder(1) }
                UiButton { text: "Remove binding"; Layout.fillWidth: true; onClicked: authoring.edit("deformer.remove",{binding:bindingPanel.binding.id}) }
            }
        }
    }
}
