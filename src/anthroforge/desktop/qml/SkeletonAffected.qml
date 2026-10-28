import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    required property var service
    UiField { id: search; Layout.fillWidth: true; placeholderText: "Search affected bones, fibers and tissues" }
    ListView {
        Layout.fillWidth: true; Layout.fillHeight: true; clip: true; reuseItems: true
        model: (panel.service.state.comparison?.rows || []).filter(r=>r.name.toLowerCase().includes(search.text.toLowerCase()))
        ScrollBar.vertical: ScrollBar {}
        delegate: ColumnLayout {
            required property var modelData
            width: ListView.view.width-14
            UiButton { text: modelData.name; Layout.fillWidth: true; alignLeft: true; checked: modelData.id===panel.service.state.selection; onClicked: panel.service.select(modelData.id) }
            UiButton { text: "Check geometry"; visible: modelData.after?.geometry?.kind==="MESH"; hint: "Run advisory checks on this candidate's accepted surface"; onClicked: panel.service.option("geometry_checks",[modelData.id]) }
            Label { Layout.fillWidth: true; text: modelData.changes.join(", ") || "Unchanged"; color: Theme.muted; wrapMode: Text.Wrap }
            Label { Layout.fillWidth: true; text: modelData.distance?.material ? "Material displacement max · "+modelData.distance.material.maximum.toPrecision(4)+" m" : ""; visible: !!text; color: Theme.text; wrapMode: Text.Wrap }
            Label { Layout.fillWidth: true; text: modelData.distance?.geometric ? "Sampled surface distance max · "+modelData.distance.geometric.maximum.toPrecision(4)+" m" : modelData.distance?.unavailable || ""; visible: !!text; color: Theme.muted; wrapMode: Text.Wrap }
            Rectangle { Layout.fillWidth: true; implicitHeight: 1; color: Theme.border; Layout.topMargin: 4; Layout.bottomMargin: 4 }
        }
    }
    Label { Layout.fillWidth: true; wrapMode: Text.Wrap; color: Theme.muted; visible: text.length>0; text: (panel.service.state.comparison?.checks || []).map(r=>r.summary).join("\n") }
}
