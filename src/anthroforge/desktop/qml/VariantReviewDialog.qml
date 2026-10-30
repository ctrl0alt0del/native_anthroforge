import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiDialog {
    id: dialog
    readonly property var service: App.variantPanel
    readonly property var viewState: service.state
    readonly property var reviewData: JSON.parse(service.reviewJson)
    readonly property var pending: (viewState.findings || []).filter(r=>r.acknowledge && !(viewState.approved || []).includes(r.key))
    title: viewState.mode === "refresh" ? "Refresh variant supports" : "Promote variant"
    modal: true; anchors.centerIn: parent; closePolicy: Popup.CloseOnEscape
    width: Math.min(1380,parent.width-28); height: Math.min(910,parent.height-28)
    onClosed: service.cancel()
    Connections { target: dialog.service; function onRequested() { dialog.open(); } function onFinished() { dialog.close(); } }
    contentItem: ColumnLayout {
        RowLayout {
            UiCombo { model: ["Split","Before","After","Overlay"]; onActivated: dialog.service.comparison.setMode(currentText) }
            UiButton { text: "Frame all"; onClicked: dialog.service.comparison.focus("") }
            Repeater { model: ["bones","fibers","tissues","attachments","skin"]
                UiCheck { required property string modelData; text: modelData; checked: dialog.service.comparison.state.filters[modelData]; onClicked: dialog.service.comparison.filter(modelData,checked) }
            }
        }
        SplitView {
            Layout.fillWidth: true; Layout.fillHeight: true
            handle: Rectangle { implicitWidth: 6; color: Theme.border }
            ColumnLayout {
                SplitView.preferredWidth: 370; SplitView.minimumWidth: 300
                UiTabBar { id: tabs; Layout.fillWidth: true; UiTabButton { text: "Review" } UiTabButton { text: "Affected" } }
                StackLayout {
                    Layout.fillWidth: true; Layout.fillHeight: true; currentIndex: tabs.currentIndex
                    SkeletonFindings { service: dialog.service }
                    SkeletonAffected { service: dialog.service; review: dialog.reviewData }
                }
            }
            ColumnLayout {
                SplitView.fillWidth: true; SplitView.minimumWidth: 350
                RowLayout {
                    Layout.fillWidth: true; Layout.fillHeight: true
                    SkeletonViewport { Layout.fillWidth: true; Layout.fillHeight: true; service: dialog.service.comparison; side: 0; visible: ["Split","Before"].includes(service.state.mode) }
                    SkeletonViewport { Layout.fillWidth: true; Layout.fillHeight: true; service: dialog.service.comparison; side: 1; visible: service.state.mode!=="Before"; overlay: service.state.mode==="Overlay" }
                }
                SkeletonAttachments { Layout.fillWidth: true; service: dialog.service; review: dialog.reviewData }
                UiCheck { text: "Preview skin update"; enabled: !!dialog.viewState.skin?.available; hint: dialog.viewState.skin?.reason || "Deform existing final skin"; checked: !!dialog.viewState.options?.preview_skin; onClicked: dialog.service.option("preview_skin", checked) }
            }
        }
        RowLayout {
            Layout.fillWidth: true; Layout.minimumHeight: 54; Layout.maximumHeight: 54
            Label { Layout.fillWidth: true; wrapMode: Text.Wrap; color: Theme.muted; text: dialog.viewState.error || (dialog.viewState.state==="preparing" ? "Preparing anatomy and dependents…" : dialog.viewState.state==="stale" ? "Anatomy changed. Refresh the comparison." : dialog.viewState.ready ? dialog.pending.length ? "Review the remaining findings" : "Ready to apply" : "Resolve blocking findings") }
            UiButton { text: "Refresh comparison"; visible: dialog.viewState.state==="stale"; onClicked: dialog.service.prepare() }
            UiButton { text: "Cancel"; onClicked: dialog.close() }
            UiButton { text: "Apply"; primary: true; enabled: dialog.viewState.state==="ready" && !!dialog.viewState.ready && !dialog.pending.length; onClicked: dialog.service.apply() }
        }
    }
}
