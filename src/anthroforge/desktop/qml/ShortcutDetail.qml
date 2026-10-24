import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

RowLayout {
    id: detail
    property string label: ""
    property string value: ""
    Layout.fillWidth: true; Layout.preferredHeight: 24; spacing: Theme.gap
    Label { text: detail.label; color: Theme.muted; Layout.preferredWidth: 80; elide: Text.ElideRight }
    Label {
        text: detail.value; color: Theme.text
        Layout.fillWidth: true; Layout.minimumWidth: 0; elide: Text.ElideMiddle
        ToolTip.text: detail.value; ToolTip.visible: hover.hovered; ToolTip.delay: 400
        HoverHandler { id: hover }
    }
}
