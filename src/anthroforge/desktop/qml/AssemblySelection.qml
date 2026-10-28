import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    required property var choices
    spacing: Theme.gap
    UiField { Layout.fillWidth: true; placeholderText: "Search names or construction"; onTextChanged: panel.choices.filter(text,0) }
    ListView {
        objectName: "assemblySelectionList"
        Layout.fillWidth: true; Layout.fillHeight: true; clip: true; reuseItems: true
        model: panel.choices
        ScrollBar.vertical: ScrollBar {}
        delegate: RowLayout {
            required property string key; required property string label; required property string detail
            required property bool chosen; required property bool locked; required property string reason
            width: ListView.view.width-14; height: 54
            UiCheck { checked: chosen; enabled: !locked; Accessible.name: label; onClicked: panel.choices.choose(key,checked) }
            ColumnLayout {
                Layout.fillWidth: true; spacing: 1
                Label { Layout.fillWidth: true; text: label; color: Theme.text; wrapMode: Text.Wrap; maximumLineCount: 2 }
                Label { Layout.fillWidth: true; text: reason || detail; color: Theme.muted; font.pixelSize: 10; elide: Text.ElideRight; ToolTip.visible: reasonHover.hovered; ToolTip.text: text; HoverHandler { id:reasonHover } }
            }
        }
    }
    RowLayout {
        UiButton { text: "Select shown"; onClicked: panel.choices.chooseShown(true) }
        UiButton { text: "Clear shown"; onClicked: panel.choices.chooseShown(false) }
        Label { Layout.fillWidth: true; horizontalAlignment: Text.AlignRight; text: panel.choices.counts.chosen+" included"; color: Theme.muted }
    }
}
