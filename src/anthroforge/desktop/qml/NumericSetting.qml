import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

RowLayout {
    id: setting
    property string label: ""
    property string hint: ""
    property real value: 0
    property int decimals: 4
    property bool length: false
    property bool mixed: false
    readonly property real unitFactor: length ? workspace.state.unit_factor : 1
    signal edited(real value)
    Layout.fillWidth: true
    Label { text: setting.label + (setting.length ? " · " + workspace.state.display_units : ""); color: Theme.muted; Layout.fillWidth: true; elide: Text.ElideRight; ToolTip.visible: labelHover.hovered; ToolTip.text: setting.hint || text; HoverHandler { id: labelHover } }
    UiField {
        id: field; Layout.preferredWidth: 100; selectByMouse: true
        Accessible.name: setting.label
        validator: DoubleValidator { notation: DoubleValidator.StandardNotation }
        placeholderText: setting.mixed ? "Mixed" : ""
        Binding { target: field; property: "text"; when: !field.activeFocus; value: setting.mixed ? "" : (setting.value/setting.unitFactor).toFixed(setting.decimals) }
        onAccepted: focus = false
        onEditingFinished: if (text.trim() && isFinite(Number(text)) && (setting.mixed || Math.abs(Number(text)*setting.unitFactor-setting.value)>1e-9)) setting.edited(Number(text)*setting.unitFactor)
    }
}
