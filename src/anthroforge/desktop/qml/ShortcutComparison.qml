import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiSection {
    required property string shortcut
    title: "Compare changes"
    expanded: true
    RowLayout {
        UiButton { text: App.shortcutComparison.state.active ? "Replace baseline" : "Capture baseline"; onClicked: App.shortcutComparison.capture(shortcut) }
        UiButton { text: "Clear"; enabled: App.shortcutComparison.state.active; onClicked: App.shortcutComparison.clear() }
    }
    RowLayout {
        Repeater {
            model: ["Before","After","Overlay"]
            UiButton {
                required property string modelData
                text: modelData; enabled: App.shortcutComparison.state.active
                checked: App.shortcutComparison.state.mode === modelData
                onClicked: App.shortcutComparison.setMode(modelData)
            }
        }
    }
    ShortcutDetail { label: "Baseline"; value: App.shortcutComparison.state.active ? "Revision "+App.shortcutComparison.state.baseline_revision+(App.shortcutComparison.state.provisional ? " · provisional" : " · accepted outputs") : "No baseline captured" }
    UiButton { text: "Compare geometry"; enabled: App.shortcutComparison.state.active; onClicked: App.shortcutComparison.compare() }
    ShortcutDetail { label: "Comparison"; value: App.shortcutComparison.state.error || App.shortcutComparison.state.state || "empty" }
    ShortcutDetail { label: "Changes"; value: String(App.shortcutComparison.state.comparison?.changed || 0)+" objects · no vertex correspondence assumed" }
    UiCheck { text: "Include full starting project in exported reports"; checked: false; onClicked: App.inspectionExport.includeReplay(checked) }
}
