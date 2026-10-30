import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    property var propertyBase: ({})
    function propertyRef(name,component) { return propertyBase.target ? {target:propertyBase.target,path:propertyBase.path.concat([name]),component:component===undefined?null:component} : ({}); }
    required property var profile
    property bool previewing: false
    property var scaleBasis: null
    readonly property real depth: Math.max(0,...(profile.depths || []))
    signal edited(var profile)
    signal resetRequested()
    Layout.fillWidth: true; spacing: Theme.gap
    function change(key,value) { const next=Object.assign({},profile); next[key]=value; edited(next); }
    function station(key,index,value) { const values=Array.from(profile[key]); values[index]=value; change(key,values); }
    function scale(value) {
        const basis=scaleBasis || profile;
        const maximum=Math.max(...basis.depths);
        if(maximum<=0) return;
        const next=App.runtime.run("tissue.profile.scaled",{profile:basis,factor:value/maximum});
        if(next) edited(next);
    }
    UiCombo { enumLabels:true; objectName: "tissueProfileDirection"; Layout.fillWidth: true; model: ["LOCAL","SMOOTH","SECTION"]; currentIndex: Math.max(0,model.indexOf(panel.profile.direction)); onActivated: panel.change("direction",currentText) }
    NumericSetting {
        objectName: "tissueProfileDepth"; label: "Overall depth"; length: true
        minimum: 0; maximum: 10; value: panel.depth; live: !panel.previewing
        enabled: panel.depth>0 || panel.scaleBasis!==null
        hint: "Scale all four station depths proportionally. For an all-zero profile, set a station depth or reset first."
        onScrubbingChanged: panel.scaleBasis=scrubbing ? App.runtime.run("tissue.profile.scaled",{profile:panel.profile,factor:1}) : null
        onEdited: value=>panel.scale(value)
    }
    Repeater {
        model: 4
        ColumnLayout {
            required property int index
            Layout.fillWidth: true; spacing: Theme.gap
            NumericSetting { propertyReference: panel.propertyRef("depths",index); label: "Station "+(index+1)+" · depth"; length: true; value: panel.profile.depths?.[index] || 0; onEdited: value=>panel.station("depths",index,value) }
            NumericSetting { propertyReference: panel.propertyRef("peaks",index); label: "Station "+(index+1)+" · peak"; value: panel.profile.peaks?.[index] ?? 0.5; onEdited: value=>panel.station("peaks",index,value) }
        }
    }
    NumericSetting { propertyReference: panel.propertyRef("roundness"); label: "Roundness"; value: panel.profile.roundness ?? 1; onEdited: value=>panel.change("roundness",value) }
    UiButton { objectName: "tissueProfileReset"; text: "Reset profile from amount"; Layout.fillWidth: true; onClicked: panel.resetRequested() }
}
