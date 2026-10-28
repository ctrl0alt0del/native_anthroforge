import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiButton {
    id: control
    property var choices: []
    property string placeholder: "Search"
    signal chosen(var row)
    alignLeft: true
    onClicked: popup.open()
    Popup {
        id: popup
        y: control.height + 3; width: Math.max(control.width, 280); height: 330
        padding: Theme.gap; margins: Theme.gap
        onOpened: { search.text=""; search.forceActiveFocus(); }
        background: Rectangle { color: Theme.panel; border.color: Theme.border; radius: Theme.radius }
        contentItem: ColumnLayout {
            spacing: Theme.gap
            UiField { id: search; Layout.fillWidth: true; placeholderText: control.placeholder }
            ListView {
                id: list
                Layout.fillWidth: true; Layout.fillHeight: true; clip: true; reuseItems: true
                model: control.choices.filter(row=>row.name.toLowerCase().includes(search.text.toLowerCase()))
                ScrollBar.vertical: ScrollBar {}
                delegate: UiButton {
                    required property var modelData
                    width: ListView.view.width-14; alignLeft: true; text: modelData.name
                    onClicked: { control.chosen(modelData); popup.close(); }
                }
                Label { anchors.centerIn: parent; visible: !list.count; text: "No matches"; color: Theme.muted }
            }
        }
    }
}
