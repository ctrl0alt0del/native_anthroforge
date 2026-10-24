import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiDialog {
    id: dialog
    objectName: "mirrorConsumersDialog"
    parent: Overlay.overlay; anchors.centerIn: parent
    width: 480; modal: true; title: "Referenced mirrored instances"
    standardButtons: Dialog.Close
    property var consumers: []
    function show(rows) { consumers=rows; search.text=""; open(); }
    ColumnLayout {
        width: parent.width; spacing: Theme.gap
        Label { text: "Resolve these references before removing the mirrored instances."; Layout.fillWidth: true; wrapMode: Text.WordWrap; color: Theme.text }
        UiField { id: search; objectName: "mirrorConsumerSearch"; placeholderText: "Search affected consumers"; Layout.fillWidth: true }
        ListView {
            objectName: "mirrorConsumerList"
            Layout.fillWidth: true; Layout.preferredHeight: 280; clip: true
            model: dialog.consumers.filter(r=>(r.name+" "+r.reason).toLowerCase().includes(search.text.toLowerCase()))
            ScrollBar.vertical: ScrollBar {}
            delegate: UiButton {
                required property var modelData
                width: ListView.view.width; alignLeft: true
                text: modelData.name; hint: modelData.reason
                onClicked: { workspace.select(modelData.id); dialog.close(); }
            }
        }
    }
}
