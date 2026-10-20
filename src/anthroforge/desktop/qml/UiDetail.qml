import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

RowLayout {
    id: detail
    property string label: ""
    property string value: ""
    property int labelWidth: 80
    Layout.fillWidth: true; spacing: Theme.gap
    Label { text: detail.label; color: Theme.muted; Layout.preferredWidth: detail.labelWidth; wrapMode: Text.WordWrap }
    Label {
        text: detail.value; color: Theme.text; Layout.fillWidth: true; elide: Text.ElideRight
        ToolTip.visible: hovered.hovered && truncated; ToolTip.text: text
        HoverHandler { id: hovered }
    }
}
