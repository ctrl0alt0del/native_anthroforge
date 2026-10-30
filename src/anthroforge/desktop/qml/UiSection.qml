import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: section
    property string title: ""
    property string hint: ""
    property bool expanded: true
    property string stateKey: ""
    property bool restored: false
    Component.onCompleted: { if(stateKey) expanded=App.workbench.expanded(stateKey,expanded); restored=true; }
    onExpandedChanged: if(restored && stateKey) App.workbench.setExpanded(stateKey,expanded)
    default property alias contents: body.data
    spacing: Theme.gap
    Layout.fillWidth: true
    data: [
    Rectangle { Layout.fillWidth: true; implicitHeight: 1; color: Theme.border },
    RowLayout {
        Layout.fillWidth: true; spacing: 0
        UiButton {
            objectName: section.title + "Toggle"
            Layout.fillWidth: true; flatStyle: true; alignLeft: true
            text: section.title; leftPadding: 24
            Image { x: 6; anchors.verticalCenter: parent.verticalCenter; source: "icons/chevron-down.svg"; sourceSize: Qt.size(12,12); rotation: section.expanded ? 0 : -90 }
            onClicked: section.expanded = !section.expanded
            Accessible.name: section.title + (section.expanded ? ", expanded" : ", collapsed")
        }
        UiHelp { visible: !!section.hint; explanation: section.hint }
    },
    ColumnLayout { id: body; visible: section.expanded; Layout.fillWidth: true; spacing: Theme.gap; Layout.bottomMargin: Theme.gap }
    ]
}
