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
            includeComparison.checked=true; includeReplay.checked=false;
            dialog.tool="rectangle"; zoom.currentIndex=0; dialog.open(); description.forceActiveFocus();
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
            UiCombo { id: zoom; objectName: "feedbackZoom"; model: ["Fit","100%"]; Layout.preferredWidth: 82; hint: "Fit the window or inspect original pixels; use scrollbars at 100%." }
            UiButton { objectName: "feedbackUndo"; text: "Undo mark"; enabled: dialog.editable && feedback.state.count>0; onClicked: feedback.undoAnnotation() }
            UiButton { objectName: "feedbackClear"; text: "Clear marks"; enabled: dialog.editable && feedback.state.count>0; onClicked: feedback.clearAnnotations() }
        }
        UiField { id: annotationText; objectName: "feedbackAnnotationText"; visible: dialog.tool==="text"; Layout.fillWidth: true; placeholderText: "Text to place · then click the screenshot"; maximumLength: 2000; enabled: dialog.editable }
        Rectangle {
            Layout.fillWidth: true; Layout.fillHeight: true; Layout.minimumHeight: 160
            color: Theme.background; border.color: Theme.border; radius: Theme.radius; clip: true
            Flickable {
                id: imageView; objectName: "feedbackImageView"; anchors.fill: parent; anchors.margins: 2; clip: true
                contentWidth: canvas.width; contentHeight: canvas.height; boundsBehavior: Flickable.StopAtBounds
                ScrollBar.vertical: ScrollBar {}
                ScrollBar.horizontal: ScrollBar {}
                FeedbackCanvas { id: canvas; objectName: "feedbackCanvas"; editor: feedback
                    width: zoom.currentIndex===0 ? imageView.width : Math.max(imageView.width,feedback.state.width)
                    height: zoom.currentIndex===0 ? imageView.height : Math.max(imageView.height,feedback.state.height)
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
        }
        RowLayout {
            Label { text: "Report type"; color: Theme.muted }
            UiCombo { id: category; objectName: "feedbackCategory"; model: ["Bug","Recommendation"]; enabled: dialog.editable; Layout.preferredWidth: 190 }
            Label { text: zoom.currentIndex===0 ? "Drag to mark · click to place text" : "Scroll to inspect · drag to mark"; color: Theme.muted; Layout.fillWidth: true; horizontalAlignment: Text.AlignRight }
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
        RowLayout {
            visible: !!feedback.state.comparison
            UiCheck { id: includeComparison; text: "Include comparison"; checked: true; enabled: dialog.editable; onClicked: feedback.comparisonOptions(checked,includeReplay.checked) }
            UiCheck { id: includeReplay; text: "Include full starting project for replay"; checked: false; enabled: dialog.editable && includeComparison.checked; onClicked: feedback.comparisonOptions(includeComparison.checked,checked) }
        }
        Label {
            objectName: "feedbackStatus"; Layout.fillWidth: true; wrapMode: Text.WrapAnywhere
            color: feedback.state.error ? Theme.danger : feedback.state.saved ? Theme.success : Theme.muted
            text: feedback.state.error || (feedback.state.busy ? "Submitting report…" : feedback.state.saved ? "Report submitted: "+feedback.state.location : feedback.state.destination)
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
