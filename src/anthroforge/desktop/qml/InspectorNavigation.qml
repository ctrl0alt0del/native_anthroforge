import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: navigation
    required property var header
    spacing: 0
    Layout.preferredWidth: 34
    Layout.fillHeight: true
    Repeater {
        model: ["Shape", "Shortcuts", "Inspect", "Skin"]
        UiTabButton {
            required property string modelData
            objectName: modelData.toLowerCase()+"Tab"
            text: modelData; vertical: true
            Layout.fillWidth: true; Layout.preferredHeight: 92
            checked: navigation.header.page===modelData
            onClicked: navigation.header.choose(modelData)
        }
    }
    Item { Layout.fillHeight: true }
}
