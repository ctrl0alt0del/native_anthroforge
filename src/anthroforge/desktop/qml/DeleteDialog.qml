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
    property var impact: ({})
    title: "Delete “" + (target?.name || "") + "”?"
    function request(entity) {
        const row = workspace.objectRecord(entity);
        if (!row || row.readonly || workspace.state.waiting) return;
        const blockers=workspace.run("mirror.source.removal.inspect",{target:entity});
        if (blockers?.length) { affected.show(blockers); return; }
        const plan = workspace.run("object.delete.inspect",{target:entity});
        if (!plan) return;
        target = row; impact = plan;
        if (!plan.affected.length) { execute(); return; }
        const children = workspace.treeRows.filter(item => item.parent === entity).length;
        explanation = row.is_tissue ? "Remove this tissue. Its construction sources remain editable. Resolve incoming attachments before deletion." : row.is_construction ? "Remove this construction object. Referenced curves must be disconnected from their consumers first." : row.is_control ? "Remove this shared control and its bindings. Its primitives remain editable." :
            children ? (row.parent ? "Preserve its children and move them to its parent." : "Replace it with an empty grouping root and preserve all children.") : "Remove this SCP.";
        open();
    }
    function execute() {
        const result = workspace.run(impact.operation, impact.arguments);
        if (typeof result === "string" && result) workspace.select(result);
    }
    Label { width: parent.width; text: dialog.explanation + "\n\nAffected: " + (dialog.impact.affected || []).map(r=>r.name).join(", ") + "\n\nYou can undo this action."; wrapMode: Text.WordWrap; color: Theme.text }
    onAccepted: execute()
    AffectedConsumersDialog { id: affected }
}
