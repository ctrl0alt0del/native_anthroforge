import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: section
    property string title: ""
    property bool expanded: true
    default property alias contents: body.data
    spacing: 8
    Layout.fillWidth: true
    data: [
    Rectangle { Layout.fillWidth: true; implicitHeight: 1; color: Theme.border },
    UiButton {
        objectName: section.title + "Toggle"
        Layout.fillWidth: true; flatStyle: true; alignLeft: true
        text: (section.expanded ? "▾  " : "▸  ") + section.title
        onClicked: section.expanded = !section.expanded
        Accessible.name: section.title + (section.expanded ? ", expanded" : ", collapsed")
    },
    ColumnLayout { id: body; visible: section.expanded; Layout.fillWidth: true; spacing: 7; Layout.bottomMargin: 5 }
    ]
}
