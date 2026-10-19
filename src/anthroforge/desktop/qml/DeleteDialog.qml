import QtQuick
import QtQuick.Controls

UiDialog {
    id: dialog
    objectName: "deleteDialog"
    parent: Overlay.overlay
    anchors.centerIn: parent
    width: 420
    modal: true
    standardButtons: Dialog.Ok | Dialog.Cancel
    property var target: ({})
    property string explanation: ""
    title: "Delete “" + (target?.name || "") + "”?"
    function request(entity) {
        const row = workspace.objectRecord(entity);
        if (!row || row.readonly || workspace.state.waiting) return;
        target = row;
        const children = workspace.treeRows.filter(item => item.parent === entity).length;
        explanation = row.is_tissue ? "Remove this tissue. Its construction sources remain editable. Resolve incoming attachments before deletion." : row.is_construction ? "Remove this construction object. Referenced curves must be disconnected from their consumers first." : row.is_control ? "Remove this shared control and its bindings. Its primitives remain editable." :
            children ? (row.parent ? "Preserve its children and move them to its parent." : "Replace it with an empty grouping root and preserve all children.") : "Remove this SCP.";
        open();
    }
    Label { width: parent.width; text: dialog.explanation + "\n\nYou can undo this action."; wrapMode: Text.WordWrap; color: Theme.text }
    onAccepted: {
        const authored = target.is_construction || target.is_tissue;
        const operation = authored ? "object.delete" : target.is_control ? "control.delete" : "scp.delete";
        const arguments = authored ? {target:target.id} : target.is_control ? {control:target.id} : {entity:target.id};
        const result = workspace.run(operation, arguments);
        if (!target.is_control && result) workspace.select(result);
    }
}
