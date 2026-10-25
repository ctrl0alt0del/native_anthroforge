import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiDialog {
    id: dialog
    objectName:"fiberPinReview"
    property string curve:""
    property var rows:[]
    property var selected:[]
    property int offset:0
    property int total:0
    property bool complete:false
    title:"Review Fiber pin repairs"; modal:true; anchors.centerIn:parent
    width:Math.min(720,parent.width-40); height:Math.min(540,parent.height-40)
    standardButtons:Dialog.NoButton
    function request(target) {
        curve=target; offset=0; selected=[];
        const args=target ? {curves:[target]} : {};
        if(workspace.run("fiber.pins.check",args)) { open(); reload(); }
    }
    function reload() {
        const filters={provider:"fiber_pins.v1"};
        if(curve) filters.scope=curve;
        const report=workspace.run("issues.list",{filters:filters,offset:offset,limit:100});
        if(!report) return;
        rows=report.records || []; total=report.total || 0;
        const checks=(report.checks || []).filter(r=>r.provider==="fiber_pins.v1" && (!curve || r.scope===curve));
        complete=checks.length>0 && checks.every(r=>r.status==="COMPLETE");
    }
    function toggle(identity,checked) { selected=selected.filter(k=>k!==identity); if(checked) selected=selected.concat([identity]); }
    function selectPage() { selected=Array.from(new Set(selected.concat(rows.filter(r=>r.evidence?.proposal && r.freshness==="current").map(r=>r.id)))); }
    Connections { target:workspace.issuePanel; function onChanged() { if(dialog.visible) dialog.reload(); } }
    contentItem:ColumnLayout {
        spacing:Theme.gap
        Label { Layout.fillWidth:true; text:dialog.complete ? (dialog.total ? "Approve the repairs to apply. No bindings change until you apply them." : "No invalid pins found.") : "Checking bindings… Existing geometry remains visible."; color:Theme.text; wrapMode:Text.Wrap }
        RowLayout {
            UiField { id:search; placeholderText:"Filter this page"; Layout.fillWidth:true }
            UiButton { objectName:"selectFiberPinPage"; text:"Select page"; enabled:dialog.complete; onClicked:dialog.selectPage() }
        }
        ListView {
            Layout.fillWidth:true; Layout.fillHeight:true; clip:true; model:dialog.rows
            ScrollBar.vertical:ScrollBar {}
            delegate:ColumnLayout {
                required property var modelData
                width:ListView.view.width-16
                visible:!search.text || modelData.summary.toLowerCase().includes(search.text.toLowerCase())
                height:visible ? implicitHeight+Theme.gap : 0
                UiCheck { Layout.fillWidth:true; text:modelData.summary; enabled:!!modelData.evidence?.proposal && modelData.freshness==="current"; checked:dialog.selected.includes(modelData.id); onClicked:dialog.toggle(modelData.id,checked) }
                Label { Layout.fillWidth:true; color:Theme.muted; wrapMode:Text.WrapAnywhere; text:modelData.evidence?.proposal ? (modelData.evidence.old_target+" / "+modelData.evidence.old_role+" → "+modelData.evidence.proposal.target+" / "+modelData.evidence.proposal.role) : modelData.details }
            }
        }
        RowLayout {
            Label { text:(dialog.offset+1)+"–"+Math.min(dialog.offset+100,dialog.total)+" / "+dialog.total; color:Theme.muted }
            UiButton { text:"Previous"; enabled:dialog.offset>0; onClicked:{dialog.offset=Math.max(0,dialog.offset-100);dialog.reload();} }
            UiButton { text:"Next"; enabled:dialog.offset+100<dialog.total; onClicked:{dialog.offset+=100;dialog.reload();} }
            Item { Layout.fillWidth:true }
            UiButton { text:"Cancel"; onClicked:dialog.close() }
            UiButton { objectName:"applyFiberPinRepairs"; text:"Apply selected ("+dialog.selected.length+")"; enabled:dialog.complete && dialog.selected.length>0; onClicked:{const result=workspace.run("fiber.pins.repair",{identities:dialog.selected});if(result!==null && result!==undefined) dialog.close();} }
        }
    }
}
