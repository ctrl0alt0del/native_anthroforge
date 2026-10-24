import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiSection {
    required property string shortcut
    title: "Compare changes"
    expanded: true
    RowLayout {
        UiButton { text: workspace.shortcutComparison.state.active ? "Replace baseline" : "Capture baseline"; onClicked: workspace.shortcutComparison.capture(shortcut) }
        UiButton { text: "Clear"; enabled: workspace.shortcutComparison.state.active; onClicked: workspace.shortcutComparison.clear() }
    }
    RowLayout {
        Repeater {
            model: ["Before","After","Overlay"]
            UiButton {
                required property string modelData
                text: modelData; enabled: workspace.shortcutComparison.state.active
                checked: workspace.shortcutComparison.state.mode === modelData
                onClicked: workspace.shortcutComparison.setMode(modelData)
            }
        }
    }
    ShortcutDetail { label: "Baseline"; value: workspace.shortcutComparison.state.active ? "Revision "+workspace.shortcutComparison.state.baseline_revision+(workspace.shortcutComparison.state.provisional ? " · provisional" : " · accepted outputs") : "No baseline captured" }
    UiButton { text: "Compare geometry"; enabled: workspace.shortcutComparison.state.active; onClicked: workspace.shortcutComparison.compare() }
    ShortcutDetail { label: "Comparison"; value: workspace.shortcutComparison.state.error || workspace.shortcutComparison.state.state || "empty" }
    ShortcutDetail { label: "Changes"; value: String(workspace.shortcutComparison.state.comparison?.changed || 0)+" objects · no vertex correspondence assumed" }
    UiCheck { text: "Include full starting project in exported reports"; checked: false; onClicked: workspace.inspectionExport.includeReplay(checked) }
}
