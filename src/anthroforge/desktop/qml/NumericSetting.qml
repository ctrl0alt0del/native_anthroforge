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
    property bool live: true
    property real step: decimals === 0 ? 1 : Math.max(length ? 0.001 : 0.01, Math.abs(value)/100)
    property real minimum: -Infinity
    property real maximum: Infinity
    readonly property real unitFactor: length ? workspace.state.unit_factor : 1
    signal edited(real value)
    Layout.fillWidth: true
    Label { text: setting.label + (setting.length ? " · " + workspace.state.display_units : ""); color: Theme.muted; Layout.fillWidth: true; elide: Text.ElideRight; ToolTip.visible: labelHover.hovered; ToolTip.text: setting.hint || text; HoverHandler { id: labelHover } }
    UiNumberField {
        id: field; Layout.preferredWidth: 100; selectByMouse: true
        objectName: setting.objectName ? setting.objectName+"Value" : "numeric"+setting.label
        Accessible.name: setting.label
        value: setting.value/setting.unitFactor; decimals: setting.decimals
        mixed: setting.mixed; live: setting.live; step: setting.step/setting.unitFactor
        minimum: setting.minimum/setting.unitFactor; maximum: setting.maximum/setting.unitFactor
        onEdited: value => setting.edited(value*setting.unitFactor)
    }
}
