import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiSection {
    id: editor
    required property var selected
    objectName: "objectTransform"
    enabled: !!selected.transformable && !selected.readonly && !workspace.state.waiting
    title: selected.parent ? "Local transform" : "Transform"
    function setGroup(group,values) {
        const transformed=selected.local_trs.slice();
        transformed.splice(group*3,3,...values);
        workspace.run("object.transform",{target:selected.id,values:transformed});
    }
    VectorSetting { label: "Position"; length: true; values: editor.selected.local_trs?.slice(0,3) || [0,0,0]; onEdited: values => editor.setGroup(0,values) }
    VectorSetting { label: "Rotation · °"; step: 1; values: editor.selected.local_trs?.slice(3,6) || [0,0,0]; onEdited: values => editor.setGroup(1,values) }
    VectorSetting { label: "Scale"; values: editor.selected.local_trs?.slice(6,9) || [1,1,1]; onEdited: values => editor.setGroup(2,values) }
}
