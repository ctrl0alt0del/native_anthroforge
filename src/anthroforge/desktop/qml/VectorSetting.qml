import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: setting
    property string label: "Position"
    property var values: [0,0,0]
    property var propertyReference: ({})
    property bool length: false
    property bool live: true
    property int decimals: 4
    property real step: length ? 0.001 : 0.01
    readonly property real unitFactor: length ? App.runtime.state.unit_factor : 1
    signal edited(var values)
    Layout.fillWidth: true
    Label { text: setting.label + (setting.length ? " · " + App.runtime.state.display_units : ""); color: Theme.muted; font.pixelSize: 11 }
    RowLayout {
        Repeater {
            model: 3
            UiNumberField {
                id: field; required property int index
                propertyReference: setting.propertyReference.target ? Object.assign({},setting.propertyReference,{component:index}) : ({})
                objectName: "vector"+setting.label+index
                Layout.fillWidth: true; Layout.preferredWidth: 75; leftPadding: 20
                value: Number(setting.values[field.index] || 0)/setting.unitFactor
                decimals: setting.decimals
                live: setting.live; step: setting.step/setting.unitFactor
                Accessible.name: setting.label+" "+["X","Y","Z"][index]
                Text { x: 5; anchors.verticalCenter: parent.verticalCenter; text: ["X","Y","Z"][field.index]; color: Theme.axes[field.index] }
                onEdited: number => {
                    number*=setting.unitFactor;
                    const value=setting.values.slice(); value[index]=number; setting.edited(value);
                }
            }
        }
    }
}
