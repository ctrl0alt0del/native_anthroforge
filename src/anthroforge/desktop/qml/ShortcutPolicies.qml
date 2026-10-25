import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiSection {
    id: panel
    objectName: "shortcutPolicies"
    required property var adapter
    title: "Attachment policy"
    expanded: false
    Label {
        Layout.fillWidth: true; wrapMode: Text.Wrap; color: Theme.muted; font.pixelSize: 11
        text: panel.adapter.ownerName ? "Attachment scope: "+panel.adapter.ownerName : (panel.adapter.scopeOptions.length > 2 ? "Choose an attachment scope for a control spanning several SCPs." : "Attachment policies require a controlled SCP.")
    }
    UiCombo {
        objectName: "shortcutAttachmentScope"; Layout.fillWidth: true
        visible: panel.adapter.scopeOptions.length > 2 || !!panel.adapter.scopeIdentity
        model: panel.adapter.scopeOptions; textRole: "label"
        currentIndex: Math.max(0,model.findIndex(v=>v.id===panel.adapter.scopeIdentity))
        onActivated: panel.adapter.setScope(model[currentIndex].id)
    }
    UiCheck {
        visible: !!panel.adapter.ownerName; text: "Preserve owner attachment location"
        checked: panel.adapter.preserveOwner
        onClicked: panel.adapter.setBacksolve(checked)
        ToolTip.visible: hovered; ToolTip.text: "Translate the owner to retain its attachment location during this shortcut edit."
    }
    UiField { visible: !!panel.adapter.ownerName; Layout.fillWidth: true; placeholderText: "Search descendants"; onTextChanged: panel.adapter.filter(text) }
    ListView {
        visible: !!panel.adapter.ownerName; Layout.fillWidth: true; Layout.preferredHeight: Math.min(290,count*150)
        model: panel.adapter.descendants; clip: true; spacing: 8; ScrollBar.vertical: ScrollBar {}
        delegate: ColumnLayout {
            id: row
            required property string target
            required property string label
            required property var policy
            width: ListView.view.width-16; height: implicitHeight; spacing: 2
            Label { text: row.label; color: Theme.text; Layout.fillWidth: true; wrapMode: Text.Wrap }
            Repeater {
                model: [
                    {key:"parent_anchor",label:"Parent anchor",values:["KEEP","SURFACE_NEAREST","OBJECT_ORIGIN"]},
                    {key:"child_anchor",label:"Child anchor",values:["KEEP","FACE_CENTER","VERTEX_NEAREST","OBJECT_ORIGIN"]},
                    {key:"follow_rotation",label:"Follow rotation",values:["KEEP","ENABLED","DISABLED"]},
                    {key:"strategy",label:"Rotation strategy",values:["KEEP","AUTO","STABLE_SURFACE","DEFORMATION_FLOW"]}
                ]
                RowLayout {
                    required property var modelData
                    Layout.fillWidth: true
                    Label { text: modelData.label; color: Theme.muted; font.pixelSize: 10; Layout.preferredWidth: 92 }
                    UiCombo { Layout.fillWidth: true; model: modelData.values; currentIndex: model.indexOf(row.policy[modelData.key]); onActivated: panel.adapter.override(row.target,modelData.key,currentText) }
                }
            }
        }
    }
}
