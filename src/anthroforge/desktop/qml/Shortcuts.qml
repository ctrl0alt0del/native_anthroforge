import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    property var adapter: workspace.shortcutPanel
    property bool allObjects: false
    property bool choosing: false
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
    UiField { id: search; Layout.fillWidth: true; placeholderText: "Search shortcuts"; onTextChanged: panel.refresh() }
    UiButton {
        text: panel.choosing ? "Close property list" : "Expose property"; Layout.fillWidth: true
        onClicked: { panel.choosing=!panel.choosing; if(panel.choosing) panel.adapter.discover(""); }
    }
    ColumnLayout {
        visible: panel.choosing; Layout.fillWidth: true; spacing: 4
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
        clip: true; spacing: 12; model: panel.adapter.rows
        ScrollBar.vertical: ScrollBar {}
        delegate: ColumnLayout {
            id: row
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
                UiButton { text: "×"; flatStyle: true; hint: "Hide shortcut; formulas stay active"; onClicked: panel.adapter.expose(row.reference, row.label, false) }
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
                            workspace.run("shortcut.set",{reference:row.reference,value:value,component:row.values.length>1 ? index : null});
                        }
                        ToolTip.text: row.reason || (row.dimension === "LENGTH" ? "Metres" : row.dimension === "ANGLE" ? "Radians" : "Drag or type a value")
                    }
                }
            }
        }
        Label { anchors.centerIn: parent; width: parent.width-16; visible: list.count===0; text: "Expose the properties you use for anatomical editing."; wrapMode: Text.Wrap; horizontalAlignment: Text.AlignHCenter; color: Theme.muted }
    }
}
