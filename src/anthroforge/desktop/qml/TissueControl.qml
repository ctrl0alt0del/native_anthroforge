import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    required property var inflation
    signal edited(string key,var value)
    signal resetRequested()
    Layout.fillWidth: true; spacing: Theme.gap
    UiCombo { Layout.fillWidth: true; model: ["GAUSSIAN","LINEAR","SMOOTH"]; currentIndex: Math.max(0,model.indexOf(panel.inflation.falloff)); onActivated: panel.edited("falloff",currentText) }
    NumericSetting { label: "Falloff radius"; length: true; value: panel.inflation.falloff_radius || 0; onEdited: value=>panel.edited("falloff_radius",value) }
    NumericSetting { label: "Direction depth"; length: true; value: panel.inflation.direction_depth || 0; onEdited: value=>panel.edited("direction_depth",value) }
    UiButton { objectName: "tissueControlReset"; text: "Set control at source center"; Layout.fillWidth: true; onClicked: panel.resetRequested() }
    Repeater {
        model: panel.inflation.control?.length ? ["X","Y","Z"] : []
        NumericSetting { required property string modelData; required property int index; label: "Control "+modelData; length: true; value: panel.inflation.control[index]; onEdited: value=>{const point=Array.from(panel.inflation.control); point[index]=value; panel.edited("control",point);} }
    }
}
