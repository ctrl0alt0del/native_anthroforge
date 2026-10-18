import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiSection {
    id: panel
    required property var item
    title: "Source curves"
    function update(curve,key,value) { const args={target:item.id,curve:curve}; args[key]=value; workspace.run("surface.source",args); }
    function move(index,step) { const ids=item.uses.map(use=>use.curve); const other=index+step; if(other<0 || other>=ids.length) return; [ids[index],ids[other]]=[ids[other],ids[index]]; workspace.run("surface.order",{target:item.id,curves:ids}); }
    Repeater {
        model: panel.item.uses || []
        ColumnLayout {
            required property var modelData
            required property int index
            Layout.fillWidth: true; spacing: Theme.gap
            RowLayout {
                UiButton { Layout.fillWidth: true; text: workspace.objectRecord(modelData.curve).name || "Curve"; onClicked: workspace.select(modelData.curve) }
                UiButton { text: "↑"; enabled: index>0; onClicked: panel.move(index,-1) }
                UiButton { text: "↓"; enabled: index+1<panel.item.uses.length; onClicked: panel.move(index,1) }
            }
            UiCombo { Layout.fillWidth: true; model: [{name:"Shape and transform",id:"SHAPE_AND_TRANSFORM"},{name:"Shape only",id:"SHAPE_ONLY"}]; textRole:"name"; valueRole:"id"; currentIndex:indexOfValue(modelData.mode); onActivated: panel.update(modelData.curve,"mode",currentValue) }
            UiCheck { text: "Reverse direction"; checked: modelData.reverse; onClicked: panel.update(modelData.curve,"reverse",checked) }
            NumericSetting { label:"Uniform samples"; value:modelData.samples; decimals:0; enabled:!panel.item.exact; onEdited: value=>panel.update(modelData.curve,"samples",Math.round(value)) }
            NumericSetting { label:"Start fraction"; value:modelData.start || 0; onEdited: value=>panel.update(modelData.curve,"start",value) }
            NumericSetting { label:"Span fraction"; value:modelData.span ?? 1; onEdited: value=>panel.update(modelData.curve,"span",value) }
        }
    }
}
