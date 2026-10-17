import QtQuick
import QtQuick.Controls

Dialog {
    id: dialog
    objectName: "deleteDialog"
    parent: Overlay.overlay
    anchors.centerIn: parent
    width: 420
    modal: true
    standardButtons: Dialog.Ok | Dialog.Cancel
    property var target: ({})
    property string explanation: ""
    title: "Delete “" + (target.name || "") + "”?"
    function request(entity) {
        const row = workspace.treeRows.find(item => item.id === entity);
        if (!row || row.readonly || workspace.state.waiting) return;
        target = row;
        const children = workspace.treeRows.filter(item => item.parent === entity).length;
        explanation = row.is_control ? "Remove this shared control and its bindings. Its primitives remain editable." :
            children ? (row.parent ? "Preserve its children and move them to its parent." : "Replace it with an empty grouping root and preserve all children.") : "Remove this SCP.";
        open();
    }
    Label { width: parent.width; text: dialog.explanation + "\n\nYou can undo this action."; wrapMode: Text.WordWrap; color: Theme.text }
    onAccepted: {
        const result = workspace.run(target.is_control ? "control.delete" : "scp.delete", target.is_control ? {control:target.id} : {entity:target.id});
        if (!target.is_control && result) workspace.select(result);
    }
}
