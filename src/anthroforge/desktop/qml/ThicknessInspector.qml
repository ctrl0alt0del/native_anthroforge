import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiSection {
    id: panel
    property var item: ({})
    property bool topologyLocked: false
    readonly property var settings: item.thickness || {}
    title: "Thickness"; expanded: !!item.thickness
    hint: "Simple Solidify adds thickness while keeping the surface editable."
    function set(key,value) { const args={entity:item.id}; args[key]=value; authoring.edit("thickness.update",args); }
    UiButton { visible: !panel.item.thickness; text: "Add thickness"; enabled: !panel.topologyLocked; Layout.fillWidth: true; onClicked: panel.set("thickness",.01) }
    ColumnLayout {
        visible: !!panel.item.thickness; Layout.fillWidth: true
        UiCheck { text: "Enabled"; checked: panel.settings.enabled || false; enabled: !panel.topologyLocked; onClicked: panel.set("enabled",checked) }
        NumericSetting { length: true; label: "Thickness"; value: panel.settings.thickness || 0; onEdited: value => panel.set("thickness",value) }
        NumericSetting { label: "Offset · −1 to 1"; value: panel.settings.offset || 0; onEdited: value => panel.set("offset",value) }
        UiCheck { text: "Fill rim"; checked: panel.settings.rim || false; enabled: !panel.topologyLocked; onClicked: panel.set("rim",checked) }
        UiCheck { text: "Only rim"; checked: panel.settings.rim_only || false; enabled: !panel.topologyLocked; onClicked: panel.set("rim_only",checked) }
        UiCheck { text: "Even thickness"; checked: panel.settings.even || false; onClicked: panel.set("even",checked) }
        UiCheck { text: "High quality normals"; checked: panel.settings.high_quality_normals || false; onClicked: panel.set("high_quality_normals",checked) }
        UiCheck { text: "Flip normals"; checked: panel.settings.flip || false; enabled: !panel.topologyLocked; onClicked: panel.set("flip",checked) }
        NumericSetting { label: "Clamp"; value: panel.settings.clamp || 0; onEdited: value => panel.set("clamp",value) }
        UiCheck { text: "Angle clamp"; checked: panel.settings.angle_clamp || false; onClicked: panel.set("angle_clamp",checked) }
        NumericSetting { label: "Minimum weighted thickness"; value: panel.settings.minimum || 0; onEdited: value => panel.set("minimum",value) }
        UiCheck { text: "Invert weights"; checked: panel.settings.invert || false; onClicked: panel.set("invert",checked) }
        UiField { Layout.fillWidth: true; placeholderText: "Vertex weights, comma separated"; text: (panel.settings.weights || []).join(", "); onEditingFinished: panel.set("weights",text.trim()?text.split(",").map(Number):[]) }
        UiButton { text: "Remove thickness"; enabled: !panel.topologyLocked; Layout.fillWidth: true; onClicked: authoring.edit("thickness.update",{entity:panel.item.id,remove:true}) }
    }
}
