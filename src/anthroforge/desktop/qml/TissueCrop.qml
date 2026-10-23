import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiSection {
    id: panel
    property var propertyBase: ({})
    function propertyRef(name,component) { return propertyBase.target ? {target:propertyBase.target,path:propertyBase.path.concat([name]),component:component===undefined?null:component} : ({}); }
    required property var settings
    signal edited(string key,var value)
    title: "Material crop"; expanded: false
    function coordinate(key,index,value) { const point=Array.from(settings[key]); point[index]=value; edited(key,point); }
    UiCheck { objectName: "tissueCropEnabled"; text: "Enable crop"; checked: panel.settings.enabled || false; onClicked: panel.edited("enabled",checked) }
    UiCheck { text: "Keep positive half"; checked: panel.settings.positive ?? true; onClicked: panel.edited("positive",checked) }
    Repeater {
        model: ["X","Y","Z"]
        ColumnLayout {
            required property int index
            required property string modelData
            Layout.fillWidth: true; spacing: Theme.gap
            NumericSetting { propertyReference: panel.propertyRef("origin",index); label: "Origin "+modelData; length: true; value: panel.settings.origin?.[index] || 0; onEdited: value=>panel.coordinate("origin",index,value) }
            NumericSetting { propertyReference: panel.propertyRef("normal",index); label: "Normal "+modelData; value: panel.settings.normal?.[index] || 0; onEdited: value=>panel.coordinate("normal",index,value) }
        }
    }
}
