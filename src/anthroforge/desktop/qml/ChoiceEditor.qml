import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    property var rows: []
    property string title: "Choices"
    property string chosenLabel: "Selected"
    property string otherLabel: "Not selected"
    property string chooseLabel: "Select shown"
    property string clearLabel: "Clear shown"
    property string resetLabel: "Reset"
    property string summary: choices.counts.chosen+" / "+choices.counts.total+" selected"
    readonly property var choices: App.construction.createChoiceModel(panel)
    signal edited(var values)
    signal focused(string key)
    signal resetRequested()
    Layout.fillWidth: true; spacing: Theme.gap
    onRowsChanged: choices.synchronize(rows)
    Component.onCompleted: choices.synchronize(rows)
    Connections { target: panel.choices; function onEdited(values) { panel.edited(values); } }
    RowLayout {
        Layout.fillWidth: true
        ColumnLayout {
            Layout.fillWidth: true; spacing: 2
            Label { text: panel.title; color: Theme.text }
            Label { text: panel.summary; color: Theme.muted; font.pixelSize: 11; Layout.fillWidth: true; elide: Text.ElideRight }
        }
        UiButton { id: expand; objectName: panel.objectName+"Toggle"; text: checked ? "Close" : "Edit"; checkable: true }
    }
    ColumnLayout {
        visible: expand.checked; Layout.fillWidth: true; spacing: Theme.gap
        UiField { id: search; objectName: panel.objectName+"Search"; Layout.fillWidth: true; placeholderText: "Search names or context…"; onTextChanged: panel.choices.filter(text,scope.currentIndex) }
        UiCombo { id: scope; objectName: panel.objectName+"Filter"; Layout.fillWidth: true; model: ["All",panel.chosenLabel,panel.otherLabel]; onActivated: panel.choices.filter(search.text,currentIndex) }
        Rectangle {
            Layout.fillWidth: true; Layout.preferredHeight: 224; color: Theme.field; border.color: Theme.border; radius: 4
            ListView {
                id: list; objectName: panel.objectName+"List"; anchors.fill: parent; anchors.margins: 1
                model: panel.choices; clip: true; reuseItems: true; cacheBuffer: 0
                ScrollBar.vertical: ScrollBar {}
                delegate: Rectangle {
                    required property string key; required property string label; required property string detail
                    required property bool chosen; required property bool locked; required property string reason
                    width: ListView.view.width; height: 48; color: hover.hovered ? Theme.hover : "transparent"
                    HoverHandler { id: hover }
                    ToolTip.visible: hover.hovered; ToolTip.text: label+"\n"+detail+(reason ? "\n"+reason : ""); ToolTip.delay: 500
                    RowLayout {
                        anchors.fill: parent; anchors.leftMargin: Theme.gap; anchors.rightMargin: 14; spacing: Theme.gap
                        UiCheck { objectName: panel.objectName+"Choice"; property string targetId: key; checked: chosen; enabled: !locked; Accessible.name: label; onClicked: { panel.choices.choose(key,checked); panel.focused(key); } }
                        ColumnLayout {
                            Layout.fillWidth: true; spacing: 2
                            Label { text: label; color: Theme.text; Layout.fillWidth: true; elide: Text.ElideRight }
                            Label { text: reason || detail; color: Theme.muted; font.pixelSize: 10; Layout.fillWidth: true; elide: Text.ElideRight }
                        }
                    }
                    TapHandler { acceptedButtons: Qt.LeftButton; onTapped: panel.focused(key) }
                }
                Label { anchors.centerIn: parent; visible: list.count===0; text: "No matching items"; color: Theme.muted }
            }
        }
        Label { text: panel.choices.counts.shown+" shown · actions affect these rows"; font.pixelSize: 10; color: Theme.muted }
        RowLayout {
            UiButton { objectName: panel.objectName+"ChooseShown"; text: panel.chooseLabel; onClicked: panel.choices.chooseShown(true) }
            UiButton { objectName: panel.objectName+"ClearShown"; text: panel.clearLabel; onClicked: panel.choices.chooseShown(false) }
        }
        UiButton { objectName: panel.objectName+"Reset"; text: panel.resetLabel; Layout.fillWidth: true; onClicked: panel.resetRequested() }
    }
}
