import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: manager
    objectName: "workspaceManager"
    visible: false; z: 200; width: Math.min(500,parent.width-24); height: Math.min(620, parent.height-80)
    x: Math.max(0,parent.width-width-12); y: 60
    color: Theme.panel; border.color: Theme.border; radius: Theme.radius
    function open() { visible=true; }
    function close() { visible=false; }
    MouseArea { anchors.fill: parent; acceptedButtons: Qt.AllButtons }
    RowLayout {
        anchors.top: parent.top; anchors.left: parent.left; anchors.right: parent.right; anchors.margins: Theme.inset
        Label { text: "Workspace & presentation"; color: Theme.text; font.bold: true; Layout.fillWidth: true }
        UiButton { objectName: "closeWorkspace"; text: "Close"; onClicked: manager.close() }
    }
    function toggle(field,key,checked) {
        const values=App.runtime.state[field].filter(v=>v!==key);
        if(checked) values.push(key);
        const args={}; args[field]=values; App.runtime.run("workspace.update",args);
    }
    UiScrollView {
        id: scroll; anchors.fill: parent; anchors.margins: Theme.inset; anchors.topMargin: 50; clip: true; contentWidth: availableWidth
        ColumnLayout {
            width: scroll.availableWidth; spacing: Theme.inset
            RowLayout {
                WorkspaceSelector { Layout.fillWidth: true }
                UiButton { text: "Remove"; enabled: App.runtime.state.workspace>0; onClicked: App.runtime.run("workspace.remove",{index:App.runtime.state.workspace}) }
            }
            RowLayout {
                UiField { id: viewName; objectName: "workspaceName"; Layout.fillWidth: true; placeholderText: "Workspace name"; Binding { target: viewName; property: "text"; when: !viewName.activeFocus; value: App.runtime.state.workspaces[App.runtime.state.workspace] || "" } onEditingFinished: if(text.trim() && text.trim()!==App.runtime.state.workspaces[App.runtime.state.workspace]) App.runtime.run("workspace.update",{name:text.trim()}) }
            }
            RowLayout {
                Label { text: "Display units"; color: Theme.muted; Layout.fillWidth: true }
                UiHelp { explanation: "Changes displayed lengths only. Storage and API coordinates always use metres." }
                UiCombo { objectName: "displayUnits"; model: ["m","cm","mm"]; currentIndex: model.indexOf(App.runtime.state.display_units); onActivated: App.runtime.run("workspace.update",{display_units:currentText}) }
            }
            UiSection {
                title: "Presentation"
                UiCombo {
                    objectName: "workspaceMirrorDisplay"; Layout.fillWidth: true
                    model: ["Both sides", "Source only", "Mirror only"]
                    currentIndex: Math.max(0,["BOTH","SOURCE","MIRROR"].indexOf(App.runtime.state.mirror_display))
                    onActivated: App.runtime.run("workspace.update",{mirror_display:["BOTH","SOURCE","MIRROR"][currentIndex]})
                }
                UiCombo { objectName: "presentationPreset"; Layout.fillWidth: true; model: ["Choose preset…","All elements","Shape editing","Surface review","Attachment inspection"]; onActivated: { if(currentIndex) App.runtime.run("workspace.preset",{name:["","all","shape","surface","attachments"][currentIndex]}); currentIndex=0; } }
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
                            Item { Layout.preferredWidth: 48; implicitHeight: Theme.controlHeight; UiCheck { anchors.centerIn: parent; objectName: "show_"+modelData; Accessible.name: "Show "+modelData; checked: !App.runtime.state.hidden_categories.includes(modelData); onClicked: manager.toggle("hidden_categories",modelData,!checked) } }
                            Item { Layout.preferredWidth: 48; implicitHeight: Theme.controlHeight; UiCheck { anchors.centerIn: parent; objectName: "select_"+modelData; Accessible.name: "Select "+modelData; visible: modelData!=="anchors"; checked: !App.runtime.state.unpickable_categories.includes(modelData); enabled: !App.runtime.state.hidden_categories.includes(modelData); onClicked: manager.toggle("unpickable_categories",modelData,!checked) } }
                        }
                    }
                }
            }
            UiSection {
                title: "Workspace members"; expanded: false; hint: "Objects outside a focused workspace stay transparent and read-only."
                Label { text: App.runtime.state.focused ? "Choose editable objects" : "Whole document · all objects included"; color: Theme.muted; wrapMode: Text.Wrap; Layout.fillWidth: true }
                UiButton { text: "Focus selection"; enabled: !!App.selection.selectedId && !App.selection.selectedData.is_construction && !App.selection.selectedData.is_control; onClicked: App.selection.focusSelection() }
                Repeater {
                    model: App.selection.treeRows
                    UiCheck { required property var modelData; text: modelData.name+(modelData.is_control ? " · control" : " · SCP"); enabled: App.runtime.state.focused; checked: !App.runtime.state.focused || App.runtime.state.members.includes(modelData.id); onClicked: manager.toggle("members",modelData.id,checked) }
                }
            }
        }
    }
}
