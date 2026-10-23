import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: row
    required property var value
    required property var adapter
    height: 260; spacing: 3
    Label { text: row.value.expression; color: Theme.text; elide: Text.ElideRight; Layout.fillWidth: true }
    UiDetail { label: "Target"; value: (row.value.target.object_name || "Missing")+" / "+(row.value.target.label || "Unavailable") }
    UiDetail { label: "Accepted"; value: row.value.result ? String(row.value.result.value)+" · "+row.value.result.status : "Unavailable" }
    UiDetail { label: "Evidence"; value: row.value.captured_revision === null ? "Captured inputs unavailable" : "Captured revision "+row.value.captured_revision }
    UiDetail { label: "Failure"; value: row.value.result?.error || (row.value.enabled ? "None" : "Formula disabled") }
    ListView {
        Layout.fillWidth: true; Layout.preferredHeight: 112; clip: true
        model: row.value.inputs; ScrollBar.vertical: ScrollBar { policy: ScrollBar.AlwaysOn }
        delegate: ColumnLayout {
            required property var modelData
            width: ListView.view.width-14; height: 54; spacing: 0
            Label { text: modelData.name+" · "+(modelData.object_name || modelData.label || "Missing"); color: Theme.text; elide: Text.ElideMiddle; Layout.fillWidth: true }
            Label { text: "Current: "+String(modelData.value ?? "unavailable")+" · Captured: "+(modelData.captured_available ? String(modelData.captured_value) : "unavailable"); color: Theme.muted; elide: Text.ElideRight; Layout.fillWidth: true }
            Label { text: (modelData.numeric_type || "")+" · "+(modelData.dimension || "")+" · canonical m/rad"; color: Theme.muted; font.pixelSize: 10; Layout.fillWidth: true }
            TapHandler { onTapped: row.adapter.navigate(modelData.reference?.target || modelData.driver,false) }
        }
    }
    UiButton { text: row.value.participant ? "Inspect cycle" : row.value.blocked ? "Inspect blocking driver" : "Locate target"; onClicked: row.adapter.navigate(row.value.target.reference.target,false) }
}
