import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: setting
    property string label: "Position"
    property var values: [0,0,0]
    signal edited(var values)
    Layout.fillWidth: true
    Label { text: setting.label; color: Theme.muted; font.pixelSize: 11 }
    RowLayout {
        Repeater {
            model: 3
            UiField {
                id: field; required property int index
                Layout.fillWidth: true; Layout.preferredWidth: 75; leftPadding: 20
                validator: DoubleValidator { notation: DoubleValidator.StandardNotation }
                Text { x: 5; anchors.verticalCenter: parent.verticalCenter; text: ["X","Y","Z"][field.index]; color: Theme.axes[field.index] }
                Binding { target: field; property: "text"; when: !field.activeFocus; value: Number(setting.values[field.index] || 0).toFixed(4) }
                onAccepted: focus = false
                onEditingFinished: {
                    if (!text.trim() || !isFinite(Number(text)) || Math.abs(Number(text)-Number(setting.values[index]))<1e-9) return;
                    const value=setting.values.slice(); value[index]=Number(text); setting.edited(value);
                }
            }
        }
    }
}
