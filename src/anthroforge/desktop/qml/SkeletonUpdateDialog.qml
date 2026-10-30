import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiDialog {
    id: dialog
    objectName: "skeletonUpdateDialog"
    property var service: App.skeletonPanel
    readonly property var viewState: service.state
    readonly property var reviewData: JSON.parse(service.reviewJson)
    readonly property var pendingReviews: (dialog.viewState.findings || []).filter(r=>r.acknowledge && !(dialog.viewState.approved || []).includes(r.key))
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
                UiCheck { required property string modelData; text: modelData === "fibers" ? "Curves / fibers" : modelData[0].toUpperCase()+modelData.slice(1); checked: dialog.service.comparison.state.filters[modelData]; onClicked: dialog.service.comparison.filter(modelData,checked) }
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
                    SkeletonMatches { review: dialog.reviewData; service: dialog.service }
                    AssemblyMappings { service: dialog.service; allowUnresolved: false }
                    SkeletonControls { review: dialog.reviewData; service: dialog.service }
                    SkeletonAffected { review: dialog.reviewData; service: dialog.service }
                    SkeletonFindings { service: dialog.service }
                }
            }
            ColumnLayout {
                SplitView.fillWidth: true; SplitView.minimumWidth: 360
                RowLayout {
                    Layout.fillWidth: true; Layout.fillHeight: true; spacing: 2
                    SkeletonViewport { objectName: "skeletonBeforeView"; Layout.fillWidth: true; Layout.fillHeight: true; service: dialog.service.comparison; side: 0; visible: ["Split","Before"].includes(service.state.mode) }
                    SkeletonViewport { objectName: "skeletonAfterView"; Layout.fillWidth: true; Layout.fillHeight: true; service: dialog.service.comparison; side: 1; visible: service.state.mode!=="Before"; overlay: service.state.mode==="Overlay" }
                }
                SkeletonAttachments { review: dialog.reviewData; Layout.fillWidth: true; service: dialog.service }
                RowLayout {
                    UiCheck { objectName: "skeletonPreviewSkin"; text: "Preview skin update"; enabled: !!dialog.viewState.skin?.available; hint: dialog.viewState.skin?.reason || "Deform existing final skin without changing topology"; checked: !!dialog.viewState.options.preview_skin; onClicked: dialog.service.option("preview_skin",checked) }
                    Label { Layout.fillWidth: true; text: dialog.viewState.skin?.reason || (dialog.viewState.skin?.previewed ? "Skin update prepared" : dialog.viewState.skin?.retained ? "Current skin retained until updated" : ""); color: Theme.muted; wrapMode: Text.Wrap }
                }
            }
        }
        Rectangle { Layout.fillWidth: true; implicitHeight: 1; color: Theme.border }
        RowLayout {
            Layout.fillWidth: true; Layout.minimumHeight: 54; Layout.maximumHeight: 54
            Label {
                Layout.fillWidth: true; color: Theme.muted; wrapMode: Text.Wrap
                text: dialog.viewState.error || dialog.viewState.source_error || (dialog.viewState.source_state==="loading" ? "Reading replacement project…" : dialog.viewState.state==="preparing" ? "Preparing replacement and dependents…" : dialog.viewState.ready ? dialog.pendingReviews.length ? dialog.pendingReviews.length+" findings need review" : "Ready to apply as one undo action" : "Choose bone matches and resolve blocking findings")
            }
            UiButton { text: "Cancel"; onClicked: dialog.close() }
            UiButton { objectName: "skeletonApply"; text: "Apply update"; primary: true; enabled: !!dialog.viewState.ready && !dialog.pendingReviews.length; onClicked: dialog.service.apply() }
        }
    }
}
