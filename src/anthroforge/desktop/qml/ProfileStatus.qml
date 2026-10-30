import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

RowLayout {
    required property var keyboard
    spacing: 6
    Label {
        objectName: "profileStatus"
        text: App.performance.state.error ? "Recording error" : App.performance.state.recording ? "● Recording" : ["stopping", "exporting"].includes(App.performance.state.state) ? "Saving report…" : App.performance.state.state === "saved" ? "Report saved" : ""
        color: App.performance.state.recording || App.performance.state.error ? "#ed967e" : Theme.muted
        ToolTip.visible: hover.hovered
        ToolTip.text: App.performance.state.error || App.performance.state.path || (keyboard.shortcut("recordPerformance")+" stops recording and saves a performance report.")
        HoverHandler { id: hover }
    }
    UiButton {
        objectName: "recordPerformance"
        text: App.performance.state.recording ? "Stop" : App.performance.state.state === "export_failed" ? "Retry save" : "Record"
        hint: "Record performance ("+keyboard.shortcut("recordPerformance")+")"
        enabled: !["stopping", "exporting"].includes(App.performance.state.state)
        focusPolicy: Qt.NoFocus
        onClicked: App.performance.toggle()
    }
    UiButton { text: "Show file"; visible: App.performance.state.state === "saved"; focusPolicy: Qt.NoFocus; onClicked: App.performance.reveal() }
}
