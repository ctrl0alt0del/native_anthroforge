import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: activity
    spacing: 5
    ListView {
        objectName: "activityList"
        Layout.fillWidth: true; Layout.fillHeight: true
        clip: true
        model: workspace.activityModel
        spacing: 4
        delegate: RowLayout {
            id: jobRow
            required property string jobId
            required property string label
            required property string jobState
            required property string error
            required property string progress
            required property real elapsed
            required property string targets
            required property bool retryable
            required property bool cancellable
            required property string scheduling
            objectName: "activityJob-" + jobId
            width: ListView.view.width
            ColumnLayout {
                Layout.fillWidth: true
                Label { text: jobRow.label + " · " + jobRow.jobState; color: jobRow.error ? "#edab91" : "#bbcede"; elide: Text.ElideRight; Layout.fillWidth: true }
                Label { text: jobRow.error || jobRow.progress + " · " + jobRow.elapsed.toFixed(2) + " s · " + jobRow.targets; color: "#839aaf"; font.pixelSize: 10; elide: Text.ElideRight; Layout.fillWidth: true }
                Label { visible: workspace.state.diagnostics; text: jobRow.scheduling; color: Theme.muted; font.pixelSize: 10; elide: Text.ElideRight; Layout.fillWidth: true }
            }
            UiButton {
                visible: jobRow.retryable
                objectName: "retryJob-" + jobRow.jobId
                text: "Retry"
                onClicked: workspace.run("job.retry",{job_id:jobRow.jobId})
            }
            UiButton {
                visible: jobRow.cancellable
                objectName: "cancelJob-" + jobRow.jobId
                text: "Cancel"
                onClicked: workspace.run("job.cancel",{job_id:jobRow.jobId})
            }
        }
    }
}
