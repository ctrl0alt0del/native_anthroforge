import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

RowLayout {
    required property var keyboard
    spacing: 6
    Label {
        objectName: "profileStatus"
        text: performance.state.error ? "Recording error" : performance.state.recording ? "● Recording" : ["stopping", "exporting"].includes(performance.state.state) ? "Saving report…" : performance.state.state === "saved" ? "Report saved" : ""
        color: performance.state.recording || performance.state.error ? "#ed967e" : Theme.muted
        ToolTip.visible: hover.hovered
        ToolTip.text: performance.state.error || performance.state.path || (keyboard.shortcut("recordPerformance")+" stops recording and saves a performance report.")
        HoverHandler { id: hover }
    }
    UiButton {
        objectName: "recordPerformance"
        text: performance.state.recording ? "Stop" : performance.state.state === "export_failed" ? "Retry save" : "Record"
        hint: "Record performance ("+keyboard.shortcut("recordPerformance")+")"
        enabled: !["stopping", "exporting"].includes(performance.state.state)
        focusPolicy: Qt.NoFocus
        onClicked: performance.toggle()
    }
    UiButton { text: "Show file"; visible: performance.state.state === "saved"; focusPolicy: Qt.NoFocus; onClicked: performance.reveal() }
}
