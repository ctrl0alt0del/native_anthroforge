import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiDialog {
    id: dialog
    objectName: "deleteDialog"
    parent: Overlay.overlay
    anchors.centerIn: parent
    width: Math.min(520, parent.width-48)
    height: Math.min(implicitHeight, parent.height-48)
    modal: true
    standardButtons: Dialog.Ok | Dialog.Cancel
    property var target: ({})
    property string explanation: ""
    property var impact: ({})
    title: "Delete “" + (target?.name || "") + "”?"
    onAboutToShow: { search.text=""; standardButton(Dialog.Ok).text="Delete"; }
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
    contentItem: ColumnLayout {
        spacing: Theme.gap
        Label { text: dialog.explanation; Layout.fillWidth:true; wrapMode:Text.Wrap; color:Theme.text }
        Label { text:"Affected objects · "+(dialog.impact.affected || []).length; color:Theme.muted }
        UiField { id:search; objectName:"deleteAffectedSearch"; Layout.fillWidth:true; visible:(dialog.impact.affected || []).length>8; placeholderText:"Search affected objects" }
        ListView {
            objectName:"deleteAffectedObjects"; Layout.fillWidth:true; Layout.fillHeight:true
            Layout.preferredHeight:Math.min(200, (dialog.impact.affected || []).length*32); clip:true; boundsBehavior:Flickable.StopAtBounds
            model:(dialog.impact.affected || []).filter(row=>row.name.toLowerCase().includes(search.text.toLowerCase()))
            ScrollBar.vertical:ScrollBar { policy:ScrollBar.AlwaysOn }
            delegate:Label {
                required property var modelData
                width:ListView.view.width-16; padding:5; text:modelData.name
                color:Theme.text; wrapMode:Text.Wrap
            }
        }
        Label { text:"You can undo this action."; color:Theme.muted }
    }
    onAccepted: execute()
    AffectedConsumersDialog { id: affected }
}
