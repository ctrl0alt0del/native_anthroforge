import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    Layout.fillWidth: true; spacing: Theme.gap
    readonly property var tool: workspace.routeInspection
    readonly property var state: tool.state
    UiButton { objectName: "inspectRoute"; text: "Inspect route"; Layout.fillWidth: true; enabled: !["queued","running"].includes(panel.state.state); onClicked: panel.tool.start(cold.checked) }
    UiCheck { id: cold; text: "Start from planner"; checked: true; hint: "Run a separate diagnosis without a warm start. Accepted geometry stays unchanged." }
    ColumnLayout {
        Layout.fillWidth: true; visible: panel.state.visible
        UiCombo { objectName: "routeInspectionStep"; Layout.fillWidth: true; model: panel.state.labels; currentIndex: panel.state.index; onActivated: panel.tool.select(currentIndex) }
        UiCheck { text: "Contact witnesses"; checked: panel.state.showContacts; onToggled: panel.tool.setContacts(checked) }
        Label { Layout.fillWidth: true; text: panel.state.details; color: Theme.muted; wrapMode: Text.Wrap }
        Label { Layout.fillWidth: true; visible: panel.state.omitted>0; text: "Capture limit reached · "+panel.state.omitted+" records/witnesses omitted"; color: Theme.muted; wrapMode: Text.Wrap }
        UiNotice { Layout.fillWidth: true; text: panel.state.error || (panel.state.state==="stale" ? "Inputs changed; inspect again." : ""); visible: text.length>0 }
        UiButton { text: "Hide / cancel inspection"; Layout.fillWidth: true; onClicked: panel.tool.hide() }
    }
}
