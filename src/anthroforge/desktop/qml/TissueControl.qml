import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    required property var inflation
    signal edited(string key,var value)
    signal resetRequested()
    signal editRequested()
    property bool canManipulate: true
    Layout.fillWidth: true; spacing: Theme.gap
    UiCombo { Layout.fillWidth: true; model: ["GAUSSIAN","LINEAR","SMOOTH"]; currentIndex: Math.max(0,model.indexOf(panel.inflation.falloff)); onActivated: panel.edited("falloff",currentText) }
    NumericSetting { label: "Falloff radius"; length: true; value: panel.inflation.falloff_radius || 0; onEdited: value=>panel.edited("falloff_radius",value) }
    NumericSetting { label: "Direction depth"; length: true; value: panel.inflation.direction_depth || 0; onEdited: value=>panel.edited("direction_depth",value) }
    UiButton { objectName: "tissueControlReset"; text: "Set control at source center"; Layout.fillWidth: true; onClicked: panel.resetRequested() }
    UiButton { objectName: "tissueControlManipulate"; text: "Move control in viewport"; Layout.fillWidth: true; enabled: panel.canManipulate; hint: panel.canManipulate ? "Select the inflation control for the existing transform gizmo" : "Accept or cancel the preview before moving the control"; onClicked: panel.editRequested() }
    Repeater {
        model: panel.inflation.control?.length ? ["X","Y","Z"] : []
        NumericSetting { required property string modelData; required property int index; label: "Control "+modelData; length: true; value: panel.inflation.control[index]; onEdited: value=>{const point=Array.from(panel.inflation.control); point[index]=value; panel.edited("control",point);} }
    }
}
