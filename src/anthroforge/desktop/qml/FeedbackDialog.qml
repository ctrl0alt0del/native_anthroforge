import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import AnthroForge.Feedback 1.0

UiDialog {
    id: dialog
    objectName: "feedbackDialog"
    title: "Report a bug / recommendation"
    modal: true; focus: true; closePolicy: Popup.NoAutoClose
    width: Math.min(1240,parent.width-40); height: Math.min(880,parent.height-40)
    property string tool: "rectangle"
    readonly property bool editable: !feedback.state.busy && !feedback.state.saved
    onClosed: feedback.dismiss()
    Connections {
        target: feedback
        function onReady() {
            description.text=""; annotationText.text=""; category.currentIndex=0;
            dialog.tool="rectangle"; dialog.open(); description.forceActiveFocus();
        }
    }
    ColumnLayout {
        anchors.fill: parent; spacing: Theme.gap
        RowLayout {
            Layout.fillWidth: true
            Label { text: "Mark the screenshot"; color: Theme.muted }
            Repeater {
                model: [{id:"rectangle",name:"Rectangle"},{id:"arrow",name:"Arrow"},{id:"text",name:"Text"}]
                UiButton { required property var modelData; objectName: "feedbackTool_"+modelData.id; text: modelData.name; checked: dialog.tool===modelData.id; enabled: dialog.editable; onClicked: dialog.tool=modelData.id }
            }
            Item { Layout.fillWidth: true }
            UiButton { objectName: "feedbackUndo"; text: "Undo mark"; enabled: dialog.editable && feedback.state.count>0; onClicked: feedback.undoAnnotation() }
            UiButton { objectName: "feedbackClear"; text: "Clear marks"; enabled: dialog.editable && feedback.state.count>0; onClicked: feedback.clearAnnotations() }
        }
        UiField { id: annotationText; objectName: "feedbackAnnotationText"; visible: dialog.tool==="text"; Layout.fillWidth: true; placeholderText: "Text to place · then click the screenshot"; maximumLength: 2000; enabled: dialog.editable }
        Rectangle {
            Layout.fillWidth: true; Layout.fillHeight: true; Layout.minimumHeight: 160
            color: Theme.background; border.color: Theme.border; radius: Theme.radius; clip: true
            FeedbackCanvas { id: canvas; objectName: "feedbackCanvas"; anchors.fill: parent; anchors.margins: 2; editor: feedback
                MouseArea {
                    objectName: "feedbackDrawingArea"; anchors.fill: parent
                    enabled: dialog.editable; cursorShape: Qt.CrossCursor; preventStealing: true
                    onPressed: mouse=>{ mouse.accepted=canvas.begin(mouse.x,mouse.y,dialog.tool,annotationText.text); }
                    onPositionChanged: mouse=>{ if(pressed) canvas.extend(mouse.x,mouse.y); }
                    onReleased: mouse=>{ canvas.extend(mouse.x,mouse.y); feedback.finishStroke(); }
                    onCanceled: feedback.cancelStroke()
                }
            }
        }
        RowLayout {
            Label { text: "Report type"; color: Theme.muted }
            UiCombo { id: category; objectName: "feedbackCategory"; model: ["Bug","Recommendation"]; enabled: dialog.editable; Layout.preferredWidth: 190 }
            Label { text: "Drag to mark · click to place text"; color: Theme.muted; Layout.fillWidth: true; horizontalAlignment: Text.AlignRight }
        }
        UiScrollView {
            Layout.fillWidth: true; Layout.preferredHeight: 105
            TextArea {
                id: description; objectName: "feedbackDescription"; wrapMode: TextEdit.Wrap
                placeholderText: "What happened, or what would you improve? Include steps to reproduce if useful."
                color: Theme.text; placeholderTextColor: Theme.muted; selectByMouse: true
                selectionColor: Theme.selection; selectedTextColor: Theme.text; enabled: dialog.editable
                background: Rectangle { color: Theme.field; border.color: description.activeFocus ? Theme.accent : Theme.border; radius: Theme.radius }
            }
        }
        Label {
            objectName: "feedbackStatus"; Layout.fillWidth: true; wrapMode: Text.WrapAnywhere
            color: feedback.state.error ? Theme.danger : feedback.state.saved ? Theme.success : Theme.muted
            text: feedback.state.error || (feedback.state.busy ? "Submitting report…" : feedback.state.saved ? "Report saved: "+feedback.state.location : feedback.state.destination)
        }
        RowLayout {
            Layout.fillWidth: true
            UiButton { text: "Show report"; visible: feedback.state.saved; onClicked: feedback.showReport() }
            Item { Layout.fillWidth: true }
            UiButton { objectName: "feedbackCancel"; text: feedback.state.saved ? "Close" : "Cancel"; enabled: !feedback.state.busy; onClicked: dialog.close() }
            UiButton { objectName: "feedbackSubmit"; text: feedback.state.error ? "Retry submission" : "Submit report"; primary: true; visible: !feedback.state.saved; enabled: dialog.editable && description.text.trim().length>0; onClicked: feedback.submit(category.currentIndex===0 ? "bug" : "recommendation",description.text) }
        }
    }
}
