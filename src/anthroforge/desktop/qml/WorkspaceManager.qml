import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiDialog {
    id: manager
    objectName: "workspaceManager"
    title: "Workspace & presentation"; modal: true; width: 500; height: Math.min(620, parent.height-40)
    standardButtons: Dialog.Close
    function toggle(field,key,checked) {
        const values=workspace.state[field].filter(v=>v!==key);
        if(checked) values.push(key);
        const args={}; args[field]=values; workspace.run("workspace.update",args);
    }
    ScrollView {
        id: scroll; anchors.fill: parent; clip: true; contentWidth: availableWidth; rightPadding: effectiveScrollBarWidth
        ColumnLayout {
            width: scroll.availableWidth; spacing: Theme.inset
            RowLayout {
                UiCombo { Layout.fillWidth: true; model: workspace.state.workspaces; currentIndex: workspace.state.workspace; onActivated: workspace.run("workspace.select",{index:currentIndex}) }
                UiButton { text: "Remove"; enabled: workspace.state.workspace>0; onClicked: workspace.run("workspace.remove",{index:workspace.state.workspace}) }
            }
            RowLayout {
                UiField { id: viewName; objectName: "workspaceName"; Layout.fillWidth: true; placeholderText: "Workspace name"; Binding { target: viewName; property: "text"; when: !viewName.activeFocus; value: workspace.state.workspaces[workspace.state.workspace] || "" } }
                UiButton { text: "Rename"; enabled: viewName.text.trim().length>0; onClicked: workspace.run("workspace.update",{name:viewName.text.trim()}) }
            }
            RowLayout {
                Label { text: "Display units"; color: Theme.muted; Layout.fillWidth: true }
                UiHelp { explanation: "Changes displayed lengths only. Storage and API coordinates always use metres." }
                UiCombo { objectName: "displayUnits"; model: ["m","cm","mm"]; currentIndex: model.indexOf(workspace.state.display_units); onActivated: workspace.run("workspace.update",{display_units:currentText}) }
            }
            UiSection {
                title: "Presentation"
                UiCombo { objectName: "presentationPreset"; Layout.fillWidth: true; model: ["Choose preset…","All elements","Shape editing","Surface review","Attachment inspection"]; onActivated: { if(currentIndex) workspace.run("workspace.preset",{name:["","all","shape","surface","attachments"][currentIndex]}); currentIndex=0; } }
                ColumnLayout {
                    Layout.fillWidth: true; spacing: 4
                    RowLayout {
                        Layout.fillWidth: true; spacing: Theme.gap
                        Label { text: "Category"; color: Theme.muted; Layout.fillWidth: true }
                        Label { text: "Show"; color: Theme.muted; Layout.preferredWidth: 48; horizontalAlignment: Text.AlignHCenter }
                        Label { text: "Select"; color: Theme.muted; Layout.preferredWidth: 48; horizontalAlignment: Text.AlignHCenter }
                    }
                    Repeater {
                        model: ["geometry","curves","points","handles","hooks","cages","anchors"]
                        RowLayout {
                            required property string modelData
                            Layout.fillWidth: true; spacing: Theme.gap
                            Label { text: modelData.charAt(0).toUpperCase()+modelData.slice(1); Layout.fillWidth: true; color: Theme.text }
                            Item { Layout.preferredWidth: 48; implicitHeight: Theme.controlHeight; UiCheck { anchors.centerIn: parent; objectName: "show_"+modelData; Accessible.name: "Show "+modelData; checked: !workspace.state.hidden_categories.includes(modelData); onClicked: manager.toggle("hidden_categories",modelData,!checked) } }
                            Item { Layout.preferredWidth: 48; implicitHeight: Theme.controlHeight; UiCheck { anchors.centerIn: parent; objectName: "select_"+modelData; Accessible.name: "Select "+modelData; visible: modelData!=="anchors"; checked: !workspace.state.unpickable_categories.includes(modelData); enabled: !workspace.state.hidden_categories.includes(modelData); onClicked: manager.toggle("unpickable_categories",modelData,!checked) } }
                        }
                    }
                }
            }
            UiSection {
                title: "Workspace members"; expanded: false; hint: "Objects outside a focused workspace stay transparent and read-only."
                Label { text: workspace.state.focused ? "Choose editable objects" : "Whole document · all objects included"; color: Theme.muted; wrapMode: Text.Wrap; Layout.fillWidth: true }
                UiButton { text: "Create workspace from selected"; enabled: !!workspace.selectedId; onClicked: workspace.run("workspace.create",{name:"Focused workspace",members:[workspace.selectedId]}) }
                Repeater {
                    model: workspace.treeRows
                    UiCheck { required property var modelData; text: modelData.name+(modelData.is_control ? " · control" : " · SCP"); enabled: workspace.state.focused; checked: !workspace.state.focused || workspace.state.members.includes(modelData.id); onClicked: manager.toggle("members",modelData.id,checked) }
                }
            }
        }
    }
}
