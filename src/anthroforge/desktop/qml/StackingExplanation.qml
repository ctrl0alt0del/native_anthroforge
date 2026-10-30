import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    required property var evidence
    required property string target
    readonly property var report: evidence.report || ({})
    readonly property var order: report.order || ({})
    Layout.fillWidth: true
    UiNotice { active: panel.visible; text: panel.evidence.error || ""; error: true }
    UiNotice { active: panel.visible; text: panel.evidence.state==="queued" || panel.evidence.state==="running" ? "Preparing stacking footprints…" : panel.evidence.state==="stale" ? "Stacking evidence is out of date. Inspect the current relationship again." : "" }
    ColumnLayout {
        visible: panel.evidence.state==="ready"; Layout.fillWidth: true
        Label { Layout.fillWidth: true; color: Theme.text; wrapMode: Text.WordWrap; text: panel.report.active ? (panel.report.names?.[panel.order.underlying] || "Provider")+" supports "+(panel.report.names?.[panel.order.covering] || "Receiver") : "This pair has no active support relationship." }
        Label { Layout.fillWidth: true; color: Theme.muted; wrapMode: Text.WordWrap; text: "Blue: provider · orange: receiver\nOutline: calculated support on intrinsic receiver\n"+(panel.report.polygons || 0)+" polygons"+(panel.report.truncated?" · display limit reached":"") }
        UiButton { text: "Hide stacking evidence"; Layout.fillWidth: true; onClicked: App.tissueInspection.hideStacking() }
    }
}
