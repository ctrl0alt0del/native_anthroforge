import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    property var adapter: workspace.shortcutPanel
    property bool allObjects: false
    property bool choosing: false
    property bool editing: !!adapter.editing.details.id
    spacing: Theme.inset
    function refresh() { adapter.configure(visible, allObjects, search.text); }
    onVisibleChanged: refresh()
    onAllObjectsChanged: refresh()
    Component.onCompleted: refresh()
    RowLayout {
        Layout.fillWidth: true
        UiButton { text: "Selected SCP/VCP"; Layout.fillWidth: true; checked: !panel.allObjects; onClicked: panel.allObjects=false }
        UiButton { text: "All"; Layout.fillWidth: true; checked: panel.allObjects; onClicked: panel.allObjects=true }
    }
    UiField { id: search; visible: !panel.editing; Layout.fillWidth: true; placeholderText: "Search shortcuts"; onTextChanged: panel.refresh() }
    RowLayout {
        visible: !panel.editing; Layout.fillWidth: true
        UiButton {
            text: panel.choosing ? "Close list" : "Expose property"; Layout.fillWidth: true
            onClicked: { panel.choosing=!panel.choosing; if(panel.choosing) panel.adapter.discover(""); }
        }
        UiButton { text: "New driver"; Layout.fillWidth: true; onClicked: { panel.allObjects=true; panel.adapter.createDriver(); } }
    }
    ColumnLayout {
        visible: panel.choosing && !panel.editing; Layout.fillWidth: true; spacing: 4
        UiField { Layout.fillWidth: true; placeholderText: "Find a numerical property"; onTextChanged: panel.adapter.discover(text) }
        ListView {
            Layout.fillWidth: true; Layout.preferredHeight: 210; clip: true
            model: panel.adapter.properties
            ScrollBar.vertical: ScrollBar {}
            delegate: UiCheck {
                required property string label
                required property var reference
                required property bool exposed
                width: ListView.view.width; text: label; checked: exposed
                onClicked: panel.adapter.expose(reference, "", checked)
            }
        }
    }
    ListView {
        id: list; objectName: "shortcutList"; Layout.fillWidth: true; Layout.fillHeight: true
        visible: !panel.editing
        clip: true; spacing: 12; model: panel.adapter.rows
        ScrollBar.vertical: ScrollBar {}
        delegate: ColumnLayout {
            id: row
            required property string key
            required property string kind
            required property string label
            required property var reference
            required property var values
            required property string numericType
            required property string dimension
            required property bool writable
            required property string reason
            required property string ownerLabel
            width: ListView.view.width; spacing: 4
            RowLayout {
                Layout.fillWidth: true
                Label { text: row.label; Layout.fillWidth: true; wrapMode: Text.Wrap; color: Theme.text }
                UiButton { text: "⋮"; flatStyle: true; hint: "Shortcut options"; onClicked: options.open() }
                UiMenu {
                    id: options
                    UiMenuItem { text: "Edit shortcut"; onTriggered: panel.adapter.editing.select(row.key) }
                    UiMenuItem { text: "Move up"; onTriggered: panel.adapter.move(row.key,-1) }
                    UiMenuItem { text: "Move down"; onTriggered: panel.adapter.move(row.key,1) }
                    UiMenuItem { text: "Hide from shortcuts"; onTriggered: panel.adapter.hide(row.key) }
                }
            }
            Label { visible: panel.allObjects; text: row.ownerLabel; color: Theme.muted; font.pixelSize: 10; wrapMode: Text.Wrap; Layout.fillWidth: true }
            GridLayout {
                columns: Math.min(3, row.values.length); Layout.fillWidth: true
                Repeater {
                    model: row.values
                    delegate: UiNumberField {
                        required property int index
                        required property real modelData
                        value: modelData; decimals: row.numericType === "INTEGER" ? 0 : 4
                        enabled: row.writable; Layout.fillWidth: true; Layout.minimumWidth: 50
                        onEdited: value => {
                            panel.adapter.editValue(row.key,row.values.length>1 ? index : -1,value,false);
                        }
                        ToolTip.text: row.reason || (row.dimension === "LENGTH" ? "Metres" : row.dimension === "ANGLE" ? "Radians" : "Drag or type a value")
                    }
                }
            }
            UiNumberField {
                visible: row.values.length>1; value: row.values.length ? row.values[0] : 0
                enabled: row.writable; Layout.fillWidth: true
                ToolTip.text: "Uniform: set all components to the same value"
                onEdited: value => panel.adapter.editValue(row.key,-1,value,true)
            }
        }
        Label { anchors.centerIn: parent; width: parent.width-16; visible: list.count===0; text: "Expose the properties you use for anatomical editing."; wrapMode: Text.Wrap; horizontalAlignment: Text.AlignHCenter; color: Theme.muted }
    }
    ShortcutEditor { visible: panel.editing; adapter: panel.adapter.editing; Layout.fillWidth: true; Layout.fillHeight: true }
}
