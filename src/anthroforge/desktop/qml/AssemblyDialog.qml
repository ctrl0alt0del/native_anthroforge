import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiDialog {
    id: dialog
    objectName: "assemblyDialog"
    property var service: workspace.assemblyPanel
    title: service.state.repair ? "Resolve imported references" : "Import Anatomy from Project"
    modal: true; anchors.centerIn: parent
    width: Math.min(1100,parent.width-40); height: Math.min(840,parent.height-40)
    closePolicy: Popup.CloseOnEscape
    onClosed: service.cancel()
    Connections { target: dialog.service; function onRequested() { dialog.open(); } function onFinished() { dialog.close(); } }
    contentItem: ColumnLayout {
        spacing: Theme.gap
        RowLayout {
            visible: !dialog.service.state.repair
            UiCheck { text: "Include attached tissues"; checked: !!dialog.service.state.options?.include_attached_tissues; onClicked: dialog.service.option("include_attached_tissues",checked) }
            Label { text: "Destination parent"; color: Theme.muted }
            UiCombo {
                objectName: "assemblyParent"; Layout.fillWidth: true
                model: dialog.service.state.parents || []; textRole: "name"; valueRole: "id"
                currentIndex: Math.max(0,(dialog.service.state.parents || []).findIndex(r=>r.id===dialog.service.state.parent))
                onActivated: dialog.service.option("parent",currentValue)
            }
            UiCheck { text: "Rebind roots"; checked: !!dialog.service.state.options?.rebind_roots; onClicked: dialog.service.option("rebind_roots",checked); hint: "Choose new attachment locations for imported SCP roots when their original parent differs" }
        }
        SplitView {
            Layout.fillWidth: true; Layout.fillHeight: true; Layout.minimumHeight: 360
            handle: Rectangle { implicitWidth: 6; color: Theme.border }
            ColumnLayout {
                visible: !dialog.service.state.repair
                SplitView.preferredWidth: 390; SplitView.minimumWidth: 260
                UiTabBar {
                    id: tabs; Layout.fillWidth: true
                    UiTabButton { text: "Anatomy" }
                    UiTabButton { text: "Construction" }
                }
                StackLayout {
                    Layout.fillWidth: true; Layout.fillHeight: true; currentIndex: tabs.currentIndex
                    AssemblySelection { choices: dialog.service.anatomyModel }
                    AssemblySelection { choices: dialog.service.constructionModel }
                }
            }
            ColumnLayout {
                SplitView.fillWidth: true; SplitView.minimumWidth: 390
                UiTabBar {
                    id: details; Layout.fillWidth: true
                    UiTabButton { text: "Mappings" }
                    UiTabButton { text: "Attachment locations"; enabled: !!dialog.service.state.evidence?.length }
                }
                StackLayout {
                    Layout.fillWidth: true; Layout.fillHeight: true; currentIndex: details.currentIndex
                    AssemblyMappings { service: dialog.service }
                    AssemblyEvidence { evidence: dialog.service.state.evidence || [] }
                }
            }
        }
        Rectangle { Layout.fillWidth: true; implicitHeight: 1; color: Theme.border }
        RowLayout {
            Layout.fillWidth: true; Layout.minimumHeight: 70; Layout.maximumHeight: 70
            ScrollView {
                Layout.fillWidth: true; Layout.fillHeight: true
                Label {
                    width: parent.width; color: Theme.muted; wrapMode: Text.Wrap
                    text: dialog.service.state.error || dialog.service.state.source_error || (dialog.service.state.findings || []).map(f=>f.message).join("\n") || (dialog.service.state.source_state==="loading" ? "Reading project…" : dialog.service.state.state==="preparing" ? "Preparing selection…" : dialog.service.state.ready ? "Ready. Source placement is preserved. " + (dialog.service.state.unresolved ? dialog.service.state.unresolved + " references will need resolving." : "") : "Select anatomy or construction to import.")
                }
            }
            UiButton { text: "Cancel"; onClicked: dialog.close() }
            UiButton { objectName: "assemblyCommit"; text: dialog.service.state.repair ? "Resolve" : "Import"; primary: true; enabled: !!dialog.service.state.ready; onClicked: dialog.service.apply() }
        }
    }
}
