import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiDialog {
    id: dialog
    objectName: "recoveryDialog"
    title: "Recover Autosave"
    modal: true; anchors.centerIn: parent
    width: Math.min(720, parent.width - 48)
    height: Math.min(540, parent.height - 48)
    standardButtons: Dialog.Close
    readonly property var browser: App.projectLibrary.recoveryBrowser
    onAboutToShow: { search.text=""; browser.refresh(); }
    ColumnLayout {
        anchors.fill: parent; spacing: Theme.gap
        Label { text: "Open a recovery copy, then Save As to keep it. Your original project stays unchanged."; color: Theme.muted; Layout.fillWidth:true; wrapMode:Text.Wrap }
        UiField { id:search; objectName:"recoverySearch"; Layout.fillWidth:true; placeholderText:"Search project names or paths"; Accessible.name:"Search recovery copies" }
        ListView {
            id: list; objectName:"recoveryCopies"; Layout.fillWidth:true; Layout.fillHeight:true
            clip:true; spacing:6; boundsBehavior:Flickable.StopAtBounds
            model: dialog.browser.state.rows.filter(row => (row.name+" "+row.origin).toLowerCase().includes(search.text.toLowerCase()))
            ScrollBar.vertical:ScrollBar { policy:ScrollBar.AlwaysOn }
            delegate: Rectangle {
                required property var modelData
                width:ListView.view.width-14; height:72; radius:Theme.radius; color:Theme.field
                RowLayout {
                    anchors.fill:parent; anchors.margins:Theme.gap; spacing:Theme.gap
                    ColumnLayout {
                        Layout.fillWidth:true; spacing:3
                        Label { text:modelData.name; color:Theme.text; font.bold:true; Layout.fillWidth:true; elide:Text.ElideRight }
                        Label { text:Qt.formatDateTime(new Date(modelData.created),"yyyy-MM-dd hh:mm:ss")+" · Revision "+modelData.revision; color:Theme.muted; font.pixelSize:11; Layout.fillWidth:true }
                        Label { text:modelData.origin || "Untitled project"; color:Theme.muted; font.pixelSize:11; Layout.fillWidth:true; elide:Text.ElideMiddle; ToolTip.visible:pathHover.hovered; ToolTip.text:text; HoverHandler { id:pathHover } }
                    }
                    UiButton { text:"Open copy"; enabled:!dialog.browser.state.busy; onClicked:{ dialog.close(); dialog.browser.openCopy(modelData.path); } }
                }
            }
            Label { anchors.centerIn:parent; text:dialog.browser.state.busy ? "Finding recovery copies…" : "No matching recovery copies"; visible:!list.count; color:Theme.muted }
        }
        RowLayout {
            Layout.fillWidth:true
            Label { Layout.fillWidth:true; color:Theme.muted; text:dialog.browser.state.message; elide:Text.ElideRight; ToolTip.visible:messageHover.hovered && !!text; ToolTip.text:text; HoverHandler { id:messageHover } }
            UiButton { text:"Open folder"; onClicked:dialog.browser.showFolder() }
            UiButton { text:"Refresh"; enabled:!dialog.browser.state.busy; onClicked:dialog.browser.refresh() }
        }
    }
}
