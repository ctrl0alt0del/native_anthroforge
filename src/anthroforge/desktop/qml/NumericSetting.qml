import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

RowLayout {
    id: setting
    property string label: ""
    property real value: 0
    property int decimals: 4
    signal edited(real value)
    Layout.fillWidth: true
    Label { text: setting.label; color: Theme.muted; Layout.fillWidth: true; elide: Text.ElideRight }
    UiField {
        id: field; Layout.preferredWidth: 100; selectByMouse: true
        Accessible.name: setting.label
        validator: DoubleValidator { notation: DoubleValidator.StandardNotation }
        Binding { target: field; property: "text"; when: !field.activeFocus; value: setting.value.toFixed(setting.decimals) }
        onAccepted: focus = false
        onEditingFinished: if (text.trim() && isFinite(Number(text)) && Math.abs(Number(text)-setting.value)>1e-9) setting.edited(Number(text))
    }
}
