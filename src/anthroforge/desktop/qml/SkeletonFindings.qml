import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    required property var service
    UiField { id: search; Layout.fillWidth: true; placeholderText: "Search affected objects and findings" }
    ListView {
        Layout.fillWidth: true; Layout.fillHeight: true; clip: true; reuseItems: true
        model: (panel.service.state.findings || []).filter(r=>(r.owner+" "+r.message).toLowerCase().includes(search.text.toLowerCase()))
        ScrollBar.vertical: ScrollBar {}
        delegate: ColumnLayout {
            required property var modelData
            width: ListView.view.width-14
            UiButton { Layout.fillWidth: true; text: modelData.owner || "Skeleton"; alignLeft: true; onClicked: panel.service.select(modelData.owner) }
            Label { Layout.fillWidth: true; text: modelData.message; wrapMode: Text.Wrap; color: modelData.blocking ? Theme.accent : Theme.text }
            UiCheck {
                text: "Rebind on replacement surface"; visible: modelData.key.startsWith("rebind:")
                checked: !!panel.service.state.options.rebind?.[modelData.key] || modelData.acknowledge
                onClicked: panel.service.decision("rebind",modelData.key,checked)
            }
            UiCheck {
                text: "Clear incompatible anchor lock"; visible: modelData.key.startsWith("lock:")
                checked: !!panel.service.state.options.clear_locks?.[modelData.owner]
                onClicked: panel.service.decision("clear_locks",modelData.owner,checked)
            }
            RowLayout {
                visible: modelData.key.startsWith("driver_value:")
                UiButton { text: "Use formula value"; onClicked: panel.service.decision("use_formula_values",modelData.key.slice(13),true) }
                UiButton { text: "Disable formula"; onClicked: panel.service.decision("disable_formulas",modelData.key.slice(13),true) }
            }
            UiCheck { text: modelData.kind === "failure" ? "Keep retained output for this failure" : "Reviewed"; visible: modelData.acknowledge; checked: (panel.service.state.approved || []).includes(modelData.key); onClicked: panel.service.acknowledge(modelData.key,checked) }
            Rectangle { Layout.fillWidth: true; implicitHeight: 1; color: Theme.border; Layout.topMargin: 5; Layout.bottomMargin: 5 }
        }
        Label { anchors.centerIn: parent; text: "No findings"; visible: !parent.count; color: Theme.muted }
    }
}
