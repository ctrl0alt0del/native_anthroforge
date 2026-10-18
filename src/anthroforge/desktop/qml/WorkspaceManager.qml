import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: manager
    objectName: "workspaceManager"
    title: "Workspace & presentation"; modal: true; width: 540; height: 650
    standardButtons: Dialog.Close
    function toggle(field,key,checked) {
        const values=workspace.state[field].filter(v=>v!==key);
        if(checked) values.push(key);
        const args={}; args[field]=values; workspace.run("workspace.update",args);
    }
    ScrollView {
        anchors.fill: parent; clip: true; contentWidth: availableWidth
        ColumnLayout {
            width: parent.width; spacing: 10
            RowLayout {
                UiCombo { Layout.fillWidth: true; model: workspace.state.workspaces; currentIndex: workspace.state.workspace; onActivated: workspace.run("workspace.select",{index:currentIndex}) }
                UiButton { text: "Remove"; enabled: workspace.state.workspace>0; onClicked: workspace.run("workspace.remove",{index:workspace.state.workspace}) }
            }
            RowLayout {
                UiField { id: viewName; objectName: "workspaceName"; Layout.fillWidth: true; placeholderText: "Workspace name"; Binding { target: viewName; property: "text"; when: !viewName.activeFocus; value: workspace.state.workspaces[workspace.state.workspace] || "" } }
                UiButton { text: "Rename"; enabled: viewName.text.trim().length>0; onClicked: workspace.run("workspace.update",{name:viewName.text.trim()}) }
            }
            RowLayout {
                Label { text: "Display lengths"; color: Theme.muted; Layout.fillWidth: true }
                UiCombo { objectName: "displayUnits"; model: ["m","cm","mm"]; currentIndex: model.indexOf(workspace.state.display_units); onActivated: workspace.run("workspace.update",{display_units:currentText}) }
            }
            Label { text: "Storage and API coordinates always use metres."; color: Theme.muted; font.pixelSize: 11 }
            UiSection {
                title: "Presentation"
                UiCombo { objectName: "presentationPreset"; Layout.fillWidth: true; model: ["Choose preset…","All elements","Shape editing","Surface review","Attachment inspection"]; onActivated: { if(currentIndex) workspace.run("workspace.preset",{name:["","all","shape","surface","attachments"][currentIndex]}); currentIndex=0; } }
                GridLayout {
                    columns: 3; Layout.fillWidth: true
                    Label { text: "Category"; color: Theme.muted; Layout.fillWidth: true }
                    Label { text: "Show"; color: Theme.muted }
                    Label { text: "Select"; color: Theme.muted }
                    Repeater {
                        model: ["geometry","curves","points","handles","hooks","cages","anchors"]
                        RowLayout {
                            required property string modelData
                            Layout.columnSpan: 3; Layout.fillWidth: true
                            Label { text: modelData; Layout.fillWidth: true; color: Theme.text }
                            UiCheck { objectName: "show_"+modelData; checked: !workspace.state.hidden_categories.includes(modelData); onClicked: manager.toggle("hidden_categories",modelData,!checked) }
                            UiCheck { objectName: "select_"+modelData; opacity: modelData==="anchors" ? 0 : 1; checked: !workspace.state.unpickable_categories.includes(modelData); enabled: modelData!=="anchors" && !workspace.state.hidden_categories.includes(modelData); onClicked: manager.toggle("unpickable_categories",modelData,!checked) }
                        }
                    }
                }
            }
            UiSection {
                title: "Workspace members"
                Label { text: workspace.state.focused ? "Unchecked objects remain transparent and read-only." : "Whole document includes every SCP and control."; color: Theme.muted; wrapMode: Text.Wrap; Layout.fillWidth: true }
                UiButton { text: "Create workspace from selected"; enabled: !!workspace.selectedId; onClicked: workspace.run("workspace.create",{name:"Focused workspace",members:[workspace.selectedId]}) }
                Repeater {
                    model: workspace.treeRows
                    UiCheck { required property var modelData; text: modelData.name+(modelData.is_control ? " · control" : " · SCP"); enabled: workspace.state.focused; checked: !workspace.state.focused || workspace.state.members.includes(modelData.id); onClicked: manager.toggle("members",modelData.id,checked) }
                }
            }
        }
    }
}
