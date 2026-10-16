import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: activity
    spacing: 5
    function targets(outputs) {
        const names={};
        for (const row of workspace.treeRows) names[row.id]=row.name;
        return outputs.map(id => names[id] || "Project").join(", ");
    }
    ListView {
        Layout.fillWidth: true; Layout.fillHeight: true
        clip: true
        model: workspace.state.jobs.slice().reverse()
        spacing: 4
        delegate: RowLayout {
            required property var modelData
            width: ListView.view.width
            ColumnLayout {
                Layout.fillWidth: true
                Label { text: modelData.label + " · " + modelData.state; color: modelData.error ? "#edab91" : "#bbcede"; elide: Text.ElideRight; Layout.fillWidth: true }
                Label { text: modelData.error || modelData.progress + " · " + modelData.elapsed.toFixed(2) + " s · " + targets(modelData.outputs); color: "#839aaf"; font.pixelSize: 10; elide: Text.ElideRight; Layout.fillWidth: true }
            }
            UiButton {
                visible: modelData.retryable
                text: "Retry"
                onClicked: workspace.run("job.retry",{job_id:modelData.id})
            }
            UiButton {
                visible: ["queued","preparing","running","publishing","cancelling"].indexOf(modelData.state) >= 0
                text: "Cancel"
                onClicked: workspace.run("job.cancel",{job_id:modelData.id})
            }
        }
    }
}
