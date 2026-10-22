import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiSection {
    id: panel
    property var propertyBase: ({})
    function propertyRef(name,component) { return propertyBase.target ? {target:propertyBase.target,path:propertyBase.path.concat([name]),component:component===undefined?null:component} : ({}); }
    required property var settings
    property var diagnostic
    signal edited(string key,var value)
    title: "Height smoothing"; expanded: false
    UiCombo { objectName: "tissueSmoothingMode"; Layout.fillWidth: true; model: ["OFF","HEIGHT"]; currentIndex: model.indexOf(panel.settings.mode); onActivated: panel.edited("mode",currentText) }
    NumericSetting { propertyReference: panel.propertyRef("radius"); label: "Radius"; length: true; value: panel.settings.radius ?? 0.2; onEdited: value=>panel.edited("radius",value) }
    NumericSetting { propertyReference: panel.propertyRef("strength"); label: "Strength"; value: panel.settings.strength ?? 0.8; onEdited: value=>panel.edited("strength",value) }
    NumericSetting { propertyReference: panel.propertyRef("maximum_change"); label: "Maximum change"; length: true; value: panel.settings.maximum_change ?? 0.05; onEdited: value=>panel.edited("maximum_change",value) }
    UiNotice { active: panel.visible; text: panel.diagnostic ? "Height smoothing · "+panel.diagnostic.status : "" }
}
