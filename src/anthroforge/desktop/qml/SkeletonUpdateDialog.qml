import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiDialog {
    id: dialog
    objectName: "skeletonUpdateDialog"
    property var service: workspace.skeletonPanel
    readonly property var pendingReviews: (service.state.findings || []).filter(r=>r.acknowledge && !(service.state.approved || []).includes(r.key))
    title: "Update Skeleton from Project"; modal: true; anchors.centerIn: parent
    width: Math.min(1380,parent.width-28); height: Math.min(910,parent.height-28)
    closePolicy: Popup.CloseOnEscape
    onClosed: service.cancel()
    Connections { target: dialog.service; function onRequested() { dialog.open(); } function onFinished() { dialog.close(); } }
    contentItem: ColumnLayout {
        spacing: Theme.gap
        RowLayout {
            Label { text: "Compare"; color: Theme.text }
            UiCombo { objectName: "skeletonViewMode"; model: ["Split","Before","After","Overlay"]; onActivated: dialog.service.comparison.setMode(currentText) }
            UiButton { text: "Frame all"; onClicked: dialog.service.comparison.focus("") }
            Repeater {
                model: ["bones","fibers","tissues","attachments","skin"]
                UiCheck { required property string modelData; text: modelData === "fibers" ? "Curves / fibers" : modelData[0].toUpperCase()+modelData.slice(1); checked: true; onClicked: dialog.service.comparison.filter(modelData,checked) }
            }
            Item { Layout.fillWidth: true }
        }
        SplitView {
            Layout.fillWidth: true; Layout.fillHeight: true; Layout.minimumHeight: 400
            handle: Rectangle { implicitWidth: 6; color: Theme.border }
            ColumnLayout {
                SplitView.preferredWidth: 410; SplitView.minimumWidth: 340; SplitView.maximumWidth: dialog.width-420
                UiTabBar {
                    id: details; Layout.fillWidth: true
                    UiTabButton { text: "Bones" }
                    UiTabButton { text: "Links" }
                    UiTabButton { text: "Controls" }
                    UiTabButton { text: "Affected" }
                    UiTabButton { text: "Review" }
                }
                StackLayout {
                    Layout.fillWidth: true; Layout.fillHeight: true; Layout.minimumWidth: 0; currentIndex: details.currentIndex
                    SkeletonMatches { service: dialog.service }
                    AssemblyMappings { service: dialog.service; allowUnresolved: false }
                    SkeletonControls { service: dialog.service }
                    SkeletonAffected { service: dialog.service }
                    SkeletonFindings { service: dialog.service }
                }
            }
            ColumnLayout {
                SplitView.fillWidth: true; SplitView.minimumWidth: 360
                RowLayout {
                    Layout.fillWidth: true; Layout.fillHeight: true; spacing: 2
                    SkeletonViewport { Layout.fillWidth: true; Layout.fillHeight: true; service: dialog.service.comparison; side: 0; visible: ["Split","Before"].includes(service.state.mode) }
                    SkeletonViewport { Layout.fillWidth: true; Layout.fillHeight: true; service: dialog.service.comparison; side: 1; visible: service.state.mode!=="Before"; overlay: service.state.mode==="Overlay" }
                }
                SkeletonAttachments { Layout.fillWidth: true; service: dialog.service }
                RowLayout {
                    UiCheck { objectName: "skeletonPreviewSkin"; text: "Preview skin update"; enabled: !!dialog.service.state.skin?.available; hint: dialog.service.state.skin?.reason || "Deform existing final skin without changing topology"; checked: !!dialog.service.state.options.preview_skin; onClicked: dialog.service.option("preview_skin",checked) }
                    Label { Layout.fillWidth: true; text: dialog.service.state.skin?.reason || (dialog.service.state.skin?.previewed ? "Skin update prepared" : dialog.service.state.skin?.retained ? "Current skin retained until updated" : ""); color: Theme.muted; wrapMode: Text.Wrap }
                }
            }
        }
        Rectangle { Layout.fillWidth: true; implicitHeight: 1; color: Theme.border }
        RowLayout {
            Layout.fillWidth: true; Layout.minimumHeight: 54; Layout.maximumHeight: 54
            Label {
                Layout.fillWidth: true; color: Theme.muted; wrapMode: Text.Wrap
                text: dialog.service.state.error || dialog.service.state.source_error || (dialog.service.state.source_state==="loading" ? "Reading replacement project…" : dialog.service.state.state==="preparing" ? "Preparing replacement and dependents…" : dialog.service.state.ready ? dialog.pendingReviews.length ? dialog.pendingReviews.length+" findings need review" : "Ready to apply as one undo action" : "Choose bone matches and resolve blocking findings")
            }
            UiButton { text: "Cancel"; onClicked: dialog.close() }
            UiButton { objectName: "skeletonApply"; text: "Apply update"; primary: true; enabled: !!dialog.service.state.ready && !dialog.pendingReviews.length; onClicked: dialog.service.apply() }
        }
    }
}
