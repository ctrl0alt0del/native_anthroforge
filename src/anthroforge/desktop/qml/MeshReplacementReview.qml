import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiDialog {
    id: dialog
    objectName:"meshReplacementReview"
    property var service:workspace.meshReplacement
    property var selected:[]
    signal chooseFile()
    readonly property var state:service.state
    title:"Review mesh replacement"; modal:true; anchors.centerIn:parent
    width:Math.min(720,parent.width-40); height:Math.min(520,parent.height-40)
    onRejected:service.cancel()
    function toggle(key,checked) { selected=checked ? selected.concat([key]) : selected.filter(k=>k!==key); }

    Connections {
        target:dialog.service
        function onFileRequested() { dialog.chooseFile(); }
        function onReviewRequested() { dialog.selected=[]; dialog.open(); }
        function onFinished() { dialog.close(); }
    }
    contentItem:ColumnLayout {
        spacing:Theme.gap
        Label { Layout.fillWidth:true; wrapMode:Text.WordWrap; color:Theme.text; text:"The replacement loses indexed correspondence. Approve the required changes below; shared controls and the SCP identity are preserved." }
        RowLayout {
            UiField { id:search; Layout.fillWidth:true; placeholderText:"Filter affected objects or changes" }
            UiButton { objectName:"approveMeshChanges"; text:"Select all"; onClicked:dialog.selected=(dialog.state.changes || []).map(c=>c.key) }
        }
        ListView {
            Layout.fillWidth:true; Layout.fillHeight:true; clip:true; model:dialog.state.changes || []
            ScrollBar.vertical:ScrollBar {}
            delegate:ColumnLayout {
                required property var modelData
                width:ListView.view.width-16
                visible:!search.text || (modelData.name+modelData.target+modelData.description).toLowerCase().includes(search.text.toLowerCase())
                height:visible ? implicitHeight+Theme.gap : 0
                UiCheck { Layout.fillWidth:true; text:modelData.description; checked:dialog.selected.includes(modelData.key); onClicked:dialog.toggle(modelData.key,checked) }
                Label { Layout.fillWidth:true; text:modelData.name || modelData.target; color:Theme.muted; elide:Text.ElideMiddle }
            }
        }
        Label { Layout.fillWidth:true; visible:dialog.state.state==="stale"; color:Theme.accent; wrapMode:Text.WordWrap; text:"Inputs changed. Reassess before applying." }
        RowLayout {
            Layout.alignment:Qt.AlignRight
            UiButton { text:"Reassess"; visible:dialog.state.state==="stale"; onClicked:dialog.service.retry() }
            UiButton { text:"Cancel"; onClicked:dialog.service.cancel() }
            UiButton { objectName:"applyMeshReplacement"; text:"Replace mesh"; enabled:dialog.state.state==="ready" && dialog.selected.length===(dialog.state.changes || []).length; onClicked:dialog.service.apply(dialog.selected) }
        }
    }
}
