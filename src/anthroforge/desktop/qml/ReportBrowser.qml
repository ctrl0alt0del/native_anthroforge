import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import AnthroForge.Feedback 1.0

UiDialog {
    id: dialog
    objectName: "reportBrowserDialog"
    title: "Your reports"
    modal: true; focus: true; closePolicy: Popup.NoAutoClose
    width: Math.min(1200,parent.width-40); height: Math.min(820,parent.height-40)
    readonly property var status: reportBrowser.state
    onOpened: { zoom.currentIndex=0; reportBrowser.refresh(); }
    onClosed: reportBrowser.dismiss()
    ColumnLayout {
        anchors.fill: parent; spacing: Theme.gap
        RowLayout {
            Layout.fillWidth: true
            Label { text: dialog.status.count + " saved reports"; color: Theme.muted }
            Item { Layout.fillWidth: true }
            UiButton { objectName: "reportsRefresh"; text: "Refresh"; enabled: !dialog.status.busy; onClicked: reportBrowser.refresh() }
        }
        RowLayout {
            Layout.fillWidth: true; Layout.fillHeight: true; spacing: Theme.inset
            Rectangle {
                Layout.preferredWidth: Math.min(285,dialog.width*0.29); Layout.fillHeight: true
                color: Theme.field; border.color: Theme.border; radius: Theme.radius
                ListView {
                    id: reports; objectName: "reportsList"; anchors.fill: parent; anchors.margins: 1
                    clip: true; reuseItems: true; spacing: 1; model: reportBrowser.reports
                    ScrollBar.vertical: ScrollBar {}
                    delegate: ItemDelegate {
                        required property string key
                        required property string title
                        required property string category
                        required property string created_at
                        required property string error
                        width: reports.width; height: 82; padding: Theme.inset
                        enabled: !dialog.status.busy; highlighted: dialog.status.key===key
                        onClicked: { zoom.currentIndex=0; reportBrowser.select(key); }
                        background: Rectangle { color: parent.highlighted ? Theme.selection : parent.hovered ? Theme.hover : "transparent" }
                        contentItem: ColumnLayout {
                            spacing: 4
                            Label { text: title; color: Theme.text; textFormat: Text.PlainText; wrapMode: Text.WrapAnywhere; maximumLineCount: 2; elide: Text.ElideRight; Layout.fillWidth: true }
                            Label { text: error ? "Unreadable report" : category + " · " + created_at.slice(0,16).replace("T"," "); color: error ? Theme.danger : Theme.muted; font.pixelSize: 11; elide: Text.ElideRight; Layout.fillWidth: true }
                        }
                    }
                    Label { anchors.centerIn: parent; visible: dialog.status.count===0; text: dialog.status.busy ? "Loading…" : "No saved reports"; color: Theme.muted }
                }
            }
            ColumnLayout {
                Layout.fillWidth: true; Layout.fillHeight: true; spacing: Theme.gap
                RowLayout {
                    Layout.fillWidth: true
                    Label { text: "Annotated screenshot"; color: Theme.muted; Layout.fillWidth: true }
                    UiCombo { id: zoom; objectName: "reportsZoom"; model: ["Fit","100%"]; Layout.preferredWidth: 82 }
                }
                Rectangle {
                    Layout.fillWidth: true; Layout.fillHeight: true; Layout.minimumHeight: 140
                    color: Theme.field; border.color: Theme.border; radius: Theme.radius; clip: true
                    Flickable {
                        id: imageView; anchors.fill: parent; anchors.margins: 1; clip: true
                        contentWidth: zoom.currentIndex===0 ? width : Math.max(width,dialog.status.width)
                        contentHeight: zoom.currentIndex===0 ? height : Math.max(height,dialog.status.height)
                        ScrollBar.horizontal: ScrollBar {}
                        ScrollBar.vertical: ScrollBar {}
                        ReportImage { objectName: "reportPreviewImage"; width: imageView.contentWidth; height: imageView.contentHeight; image: reportBrowser.image }
                    }
                    Label { anchors.centerIn: parent; visible: dialog.status.width===0; text: dialog.status.busy ? "Loading…" : "Select a report to preview"; color: Theme.muted }
                }
                UiScrollView {
                    Layout.fillWidth: true; Layout.preferredHeight: 130
                    TextArea { objectName: "reportDescription"; text: dialog.status.description; textFormat: TextEdit.PlainText; readOnly: true; selectByMouse: true; wrapMode: TextEdit.Wrap; color: Theme.text; selectionColor: Theme.selection; selectedTextColor: Theme.text; background: Rectangle { color: Theme.field; border.color: Theme.border; radius: Theme.radius } }
                }
            }
        }
        Label { objectName: "reportsStatus"; Layout.fillWidth: true; text: dialog.status.error || (dialog.status.busy ? "Working…" : dialog.status.location); textFormat: Text.PlainText; color: dialog.status.error ? Theme.danger : Theme.muted; elide: Text.ElideMiddle; ToolTip.visible: hovered.hovered && !!text; ToolTip.text: text; HoverHandler { id: hovered } }
        RowLayout {
            Layout.fillWidth: true
            UiButton { objectName: "reportsDelete"; text: "Delete report…"; glyph: "delete"; enabled: !!dialog.status.key && !dialog.status.busy; onClicked: { removal.reportKey=dialog.status.key; removal.open(); } }
            Item { Layout.fillWidth: true }
            UiButton { objectName: "reportsClose"; text: "Close"; enabled: !dialog.status.busy; onClicked: dialog.close() }
        }
    }
    UiDialog {
        id: removal; objectName: "reportDeleteConfirmation"; title: "Delete this report?"
        anchors.centerIn: parent; width: Math.min(440,dialog.width-32)
        modal: true; focus: true; closePolicy: Popup.NoAutoClose
        property string reportKey: ""
        ColumnLayout {
            anchors.fill: parent; spacing: Theme.inset
            Label { text: "The saved report and its screenshots will be permanently removed."; color: Theme.text; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            RowLayout {
                Layout.alignment: Qt.AlignRight
                UiButton { objectName: "reportDeleteCancel"; text: "Cancel"; onClicked: removal.close() }
                UiButton { objectName: "reportDeleteConfirm"; text: "Delete report"; onClicked: { const key=removal.reportKey; removal.close(); reportBrowser.deleteReport(key); } }
            }
        }
    }
}
