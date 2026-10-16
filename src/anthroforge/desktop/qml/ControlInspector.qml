import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    readonly property var item: authoring.state
    readonly property var scps: workspace.treeRows.filter(row=>!row.is_control)
    readonly property var reference: authoring.selectedComponent
    Layout.fillWidth: true; spacing: 10
    function set(key,value) { authoring.setting("control.update",key,value); }
    UiSection {
        title: "Shared control"
        Label { text: panel.item.kind || ""; color: Theme.accent }
        UiField { Layout.fillWidth: true; text: panel.item.name || ""; onEditingFinished: panel.set("name",text) }
        Label { text: "Follows"; color: Theme.muted }
        UiCombo { Layout.fillWidth: true; model: [{id:"",name:"Document frame"}].concat(panel.scps); textRole: "name"; valueRole: "id"; currentIndex: indexOfValue(panel.item.follow || ""); onActivated: authoring.edit("control.follow",{control:panel.item.id,entity:currentValue}) }
        Repeater {
            model: ["Position · m", "Rotation · °", "Scale"]
            VectorSetting { required property int index; required property string modelData; label: modelData; values: (panel.item.trs || [0,0,0,0,0,0,1,1,1]).slice(index*3,index*3+3)
                onEdited: values => { const trs=(panel.item.trs || [0,0,0,0,0,0,1,1,1]).slice(); for(let i=0;i<3;i++) trs[index*3+i]=values[i]; authoring.edit("control.transform",{control:panel.item.id,values:trs}); } }
        }
        Label { text: "Affected SCPs: " + workspace.treeRows.filter(row=>(workspace.selectedData.affected || []).indexOf(row.id)>=0).map(row=>row.name).join(", "); color: Theme.muted; wrapMode: Text.WordWrap; Layout.fillWidth: true }
        UiCombo { id: bindTarget; model: panel.scps; textRole: "name"; valueRole: "id"; Layout.fillWidth: true }
        UiButton { text: "Bind to this SCP"; Layout.fillWidth: true; enabled: !!bindTarget.currentValue; onClicked: authoring.edit("deformer.add",{control:panel.item.id,target:{owner:bindTarget.currentValue}}) }
    }
    UiSection {
        title: "Local attachment"
        UiCombo { id: support; model: workspace.treeRows.filter(row=>row.id!==panel.item.id); textRole: "name"; valueRole: "id"; Layout.fillWidth: true }
        UiCheck { id: surface; text: "Attach to support surface"; checked: true }
        RowLayout {
            UiButton { text: "Attach / recapture"; onClicked: authoring.edit("control.attach",{control:panel.item.id,support:support.currentValue,surface:surface.checked}) }
            UiButton { text: "Detach"; onClicked: authoring.edit("control.follow",{control:panel.item.id,entity:""}) }
        }
    }
    UiSection {
        title: "Lattice cage"; visible: panel.item.kind === "LATTICE"
        VectorSetting { label: "Resolution · U / V / W"; values: panel.item.resolution || [2,2,2]; onEdited: values => authoring.edit("lattice.resize",{control:panel.item.id,resolution:values.map(Math.round)}) }
        Repeater {
            model: 3
            RowLayout {
                required property int index
                Layout.fillWidth: true
                Label { text: ["U","V","W"][index]; color: Theme.muted }
                UiCombo { Layout.fillWidth: true; model: ["LINEAR","CARDINAL","CATMULL_ROM","BSPLINE"]; currentIndex: model.indexOf((panel.item.interpolation || [])[index]); onActivated: { const values=panel.item.interpolation.slice(); values[index]=currentText; panel.set("interpolation",values); } }
            }
        }
        UiCheck { text: "Outside points only"; checked: panel.item.outside || false; onClicked: panel.set("outside",checked) }
        Label { text: "Select cage points in the viewport. Shift-click adds to selection."; color: Theme.muted; Layout.fillWidth: true; wrapMode: Text.WordWrap }
        NumericSetting { label: "Select point index"; value: panel.reference.index || 0; decimals: 0; onEdited: value => { const row=authoring.componentRows.find(r=>r.index===Math.round(value)); if(row) authoring.selectComponent(row.key,false); } }
        VectorSetting { label: "Selected point · cage coordinates"; values: panel.reference.local || [0,0,0]; enabled: panel.reference.index !== undefined; onEdited: values => authoring.edit("lattice.point",{control:panel.item.id,index:panel.reference.index,position:values}) }
        UiField { Layout.fillWidth: true; placeholderText: "Cage weights, comma separated"; text: (panel.item.weights || []).join(", "); onEditingFinished: panel.set("weights",text.trim()?text.split(",").map(Number):[]) }
    }
    DeformerStack { item: panel.item; visible: panel.item.kind === "LATTICE" }
    UiButton { text: "Delete shared control…"; Layout.fillWidth: true; onClicked: deleteDialog.open() }
    Dialog {
        id: deleteDialog; parent: Overlay.overlay; modal: true; width: 390; anchors.centerIn: parent; title: "Delete shared control?"; standardButtons: Dialog.Ok | Dialog.Cancel
        Label { width: 340; wrapMode: Text.WordWrap; text: "This removes bindings from: " + workspace.treeRows.filter(row=>(workspace.selectedData.affected || []).indexOf(row.id)>=0).map(row=>row.name).join(", ") + ". Editable primitives remain." }
        onAccepted: authoring.edit("control.delete",{control:panel.item.id})
    }
}
