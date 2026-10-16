import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: outliner
    signal importRequested()
    property var collapsed: []
    readonly property var rows: workspace.treeRows
    readonly property var filtered: rows.filter(row => accepts(row))
    spacing: 8
    function accepts(row) {
        if (search.text) return row.name.toLowerCase().indexOf(search.text.toLowerCase()) >= 0;
        let parentId = row.parent;
        while (parentId) {
            if (collapsed.indexOf(parentId) >= 0) return false;
            const parent = rows.find(item => item.id === parentId);
            parentId = parent ? parent.parent : "";
        }
        return true;
    }
    function toggle(values, value) {
        const copy = values.slice(), index = copy.indexOf(value);
        if (index >= 0) copy.splice(index, 1); else copy.push(value);
        return copy;
    }
    RowLayout {
        Layout.fillWidth: true; Layout.topMargin: 3
        Label { text: "OUTLINER"; font.pixelSize: 10; font.bold: true; font.letterSpacing: 1; color: Theme.muted; Layout.fillWidth: true }
        Label { text: outliner.rows.length; color: Theme.muted; font.pixelSize: 11 }
        UiButton { glyph: "plus"; hint: "Add an empty group under the selected SCP"; enabled: !workspace.state.waiting; onClicked: workspace.run("scp.empty", {name:"Group",parent:workspace.selectedId}) }
    }
    UiField { id: search; objectName: "outlinerSearch"; Layout.fillWidth: true; placeholderText: "Search objects…"; Accessible.name: "Search hierarchy"; onAccepted: hierarchy.forceActiveFocus() }
    ListView {
        id: hierarchy
        objectName: "hierarchy"
        Layout.fillWidth: true; Layout.fillHeight: true
        model: outliner.filtered; clip: true
        ScrollBar.vertical: ScrollBar {}
        delegate: Rectangle {
            id: row
            required property var modelData
            width: hierarchy.width; height: 30; radius: 3
            color: modelData.id === workspace.selectedId ? Theme.selection : rowMouse.containsMouse ? Theme.hover : "transparent"
            MouseArea { id: rowMouse; anchors.fill: parent; hoverEnabled: true; onClicked: { hierarchy.forceActiveFocus(); workspace.select(row.modelData.id); } }
            RowLayout {
                anchors.fill: parent; spacing: 3; anchors.leftMargin: 3 + row.modelData.depth*14; anchors.rightMargin: 4
                UiButton {
                    objectName: "expand_" + row.modelData.id
                    implicitWidth: 18; implicitHeight: 22; flatStyle: true
                    text: outliner.collapsed.indexOf(row.modelData.id) >= 0 ? "▸" : "▾"
                    opacity: outliner.rows.some(item => item.parent === row.modelData.id) ? 1 : 0
                    enabled: opacity > 0; hint: "Expand or collapse children"
                    onClicked: outliner.collapsed = outliner.toggle(outliner.collapsed,row.modelData.id)
                }
                Image { source: row.modelData.asset ? "icons/mesh.svg" : "icons/folder.svg"; sourceSize: Qt.size(14,14); opacity: row.modelData.readonly ? .4 : .85 }
                Label { text: row.modelData.name; Layout.fillWidth: true; elide: Text.ElideRight; color: row.modelData.readonly ? Theme.muted : Theme.text; font.pixelSize: 12 }
                UiButton { glyph: "eye"; flatStyle: true; implicitWidth: 23; implicitHeight: 24; opacity: row.modelData.visible ? .85 : .3; hint: row.modelData.visible ? "Hide object" : "Show object"; onClicked: workspace.run("workspace.update",{hidden:outliner.toggle(workspace.state.hidden,row.modelData.id)}) }
                UiButton { glyph: "target"; flatStyle: true; implicitWidth: 23; implicitHeight: 24; opacity: row.modelData.pickable ? .85 : .3; hint: "Toggle viewport picking"; onClicked: workspace.run("workspace.update",{unpickable:outliner.toggle(workspace.state.unpickable,row.modelData.id)}) }
            }
        }
        Label { anchors.centerIn: parent; width: parent.width-12; wrapMode: Text.WordWrap; horizontalAlignment: Text.AlignHCenter; visible: !outliner.filtered.length; text: search.text ? "No matching objects" : "Your imported objects\nwill appear here."; color: Theme.muted; lineHeight: 1.5 }
    }
    RowLayout {
        Layout.fillWidth: true
        UiButton { text: "Import"; glyph: "import"; Layout.fillWidth: true; enabled: !workspace.state.waiting; onClicked: outliner.importRequested() }
        UiButton { text: "Group root"; hint: "Wrap the current root in a new assembly group"; enabled: !workspace.state.waiting; onClicked: workspace.run("scp.wrap_root",{name:"Assembly"}) }
    }
}
