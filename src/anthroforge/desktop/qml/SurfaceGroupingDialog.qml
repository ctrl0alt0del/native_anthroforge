import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiDialog {
    id: dialog
    objectName: "surfaceGroupingDialog"
    readonly property var tool: App.surfaceCreation
    readonly property var state: tool.state
    title: "Choose surface branches"; width: 490; modal: true
    anchors.centerIn: parent
    visible: !!state.curves
    standardButtons: Dialog.NoButton
    onRejected: tool.cancel()
    contentItem: ColumnLayout {
        spacing: Theme.gap
        Label { Layout.fillWidth: true; wrapMode: Text.WordWrap; color: Theme.text; text: "These connections allow more than one grouping. Assign curves to the main loft or a branch." }
        ListView {
            objectName: "surfaceGroupSources"; Layout.fillWidth: true; Layout.preferredHeight: 230
            clip: true; model: dialog.state.curves || []
            ScrollBar.vertical: ScrollBar { policy: ScrollBar.AlwaysOn }
            delegate: RowLayout {
                required property var modelData
                required property int index
                width: ListView.view.width-18; height: 38
                Label { Layout.fillWidth: true; text: modelData.name; color: Theme.text; elide: Text.ElideRight }
                UiCombo {
                    objectName: "surfaceGroupRole"+index; Layout.preferredWidth: 160
                    model: ["Main loft"].concat(Array.from({length:Math.floor((dialog.state.curves || []).length/2)},(_,i)=>"Branch "+(i+1)))
                    currentIndex: dialog.state.roles?.[modelData.id] || 0
                    onActivated: dialog.tool.assign(modelData.id,currentIndex)
                }
            }
        }
        ListView {
            Layout.fillWidth: true; Layout.preferredHeight: Math.min(120,count*38)
            clip: true; model: dialog.state.groups || []
            ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
            delegate: RowLayout {
                required property var modelData
                width: ListView.view.width-18; height: 38
                Label { text: "Branch "+modelData.number+" joins"; color: Theme.text }
                UiCombo {
                    Layout.fillWidth: true; model: modelData.boundaries; textRole: "name"; valueRole: "id"
                    currentIndex: modelData.boundaries.findIndex(b=>b.id===modelData.boundary)
                    onActivated: dialog.tool.boundary(modelData.number,currentValue)
                }
            }
        }
        Label { Layout.fillWidth: true; Layout.preferredHeight: 46; wrapMode: Text.WordWrap; color: Theme.muted; text: dialog.state.reason || "Each branch needs at least two curves. Main curves retain their selection order." }
        RowLayout {
            Item { Layout.fillWidth: true }
            UiButton { text: "Cancel"; onClicked: dialog.tool.cancel() }
            UiButton { objectName: "confirmSurfaceGrouping"; text: "Create Surface"; enabled: dialog.state.valid || false; onClicked: dialog.tool.accept() }
        }
    }
}
