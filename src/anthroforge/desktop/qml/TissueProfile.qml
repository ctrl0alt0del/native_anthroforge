import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    required property var profile
    signal edited(var profile)
    signal resetRequested()
    Layout.fillWidth: true; spacing: Theme.gap
    function change(key,value) { const next=Object.assign({},profile); next[key]=value; edited(next); }
    function station(key,index,value) { const values=Array.from(profile[key]); values[index]=value; change(key,values); }
    UiCombo { objectName: "tissueProfileDirection"; Layout.fillWidth: true; model: ["LOCAL","SMOOTH","SECTION"]; currentIndex: Math.max(0,model.indexOf(panel.profile.direction)); onActivated: panel.change("direction",currentText) }
    Repeater {
        model: 4
        ColumnLayout {
            required property int index
            Layout.fillWidth: true; spacing: Theme.gap
            NumericSetting { label: "Station "+(index+1)+" · depth"; length: true; value: panel.profile.depths?.[index] || 0; onEdited: value=>panel.station("depths",index,value) }
            NumericSetting { label: "Station "+(index+1)+" · peak"; value: panel.profile.peaks?.[index] ?? 0.5; onEdited: value=>panel.station("peaks",index,value) }
        }
    }
    NumericSetting { label: "Roundness"; value: panel.profile.roundness ?? 1; onEdited: value=>panel.change("roundness",value) }
    UiButton { objectName: "tissueProfileReset"; text: "Reset profile from amount"; Layout.fillWidth: true; onClicked: panel.resetRequested() }
}
