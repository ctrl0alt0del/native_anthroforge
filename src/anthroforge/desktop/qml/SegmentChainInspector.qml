import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiSection {
    id: panel
    property var item: ({})
    property bool topologyLocked: false
    readonly property var chain: item.primitive?.chain || {}
    readonly property var segments: chain.segments || []
    readonly property int segmentIndex: Math.max(0, segmentChoice.currentIndex)
    readonly property var segment: segments[segmentIndex] || {}
    title: "Segment chain"
    function configure(key, value) {
        const args = {entity:item.id}; args[key] = value;
        App.authoring.edit("chain.configure", args);
    }
    function setSegment(key, value) {
        const args = {entity:item.id,index:segmentIndex}; args[key] = value;
        App.authoring.edit("chain.segment", args);
    }
    NumericSetting { propertyReference: ({target:panel.item.id,path:["primitive","chain","spread"]}); objectName:"chainSpread"; label:"Spread · degrees"; value:(panel.chain.spread || 0)*180/Math.PI; onEdited:value=>panel.configure("spread",value*Math.PI/180) }
    UiCombo { Layout.fillWidth:true; model:["Adjacent bend pairs","Cumulative bends"]; currentIndex:panel.chain.bend_mode==="CUMULATIVE"?1:0; onActivated:panel.configure("bend_mode",currentIndex===1?"CUMULATIVE":"ADJACENT") }
    UiCombo { id:segmentChoice; objectName:"segmentChoice"; Layout.fillWidth:true; model:panel.segments.map((s,i)=>"Segment "+(i+1)) }
    NumericSetting { propertyReference: ({target:panel.item.id,path:["primitive","chain","segments","#"+panel.segmentIndex,"length"]}); objectName:"segmentLength"; label:"Length"; length:true; minimum:0; value:panel.segment.length || 0; onEdited:value=>panel.setSegment("length",value) }
    NumericSetting { propertyReference: ({target:panel.item.id,path:["primitive","chain","segments","#"+panel.segmentIndex,"radius"]}); objectName:"segmentRadius"; label:"Radius"; length:true; minimum:panel.segment.length>0?0.000001:0; value:panel.segment.radius ?? .05; onEdited:value=>panel.setSegment("radius",value) }
    NumericSetting { propertyReference: ({target:panel.item.id,path:["primitive","chain","segments","#"+panel.segmentIndex,"bend"]}); objectName:"segmentBend"; label:"Bend · degrees"; value:(panel.segment.bend || 0)*180/Math.PI; onEdited:value=>panel.setSegment("bend",value*Math.PI/180) }
    UiSection {
        title:"Construction settings"; expanded:false
        NumericSetting { label:"Segment count"; decimals:0; minimum:1; maximum:32; enabled:!panel.topologyLocked; value:panel.segments.length; onEdited:value=>App.authoring.edit("chain.resize",{entity:panel.item.id,count:Math.round(value)}) }
        NumericSetting { propertyReference: ({target:panel.item.id,path:["primitive","chain","segments","#"+panel.segmentIndex,"samples"]}); label:"Samples"; decimals:0; minimum:2; maximum:256; enabled:!panel.topologyLocked; value:panel.segment.samples || 10; onEdited:value=>panel.setSegment("samples",Math.round(value)) }
        NumericSetting { propertyReference: ({target:panel.item.id,path:["primitive","chain","segments","#"+panel.segmentIndex,"sides"]}); label:"Radial sides"; decimals:0; minimum:3; maximum:128; enabled:!panel.topologyLocked; value:panel.segment.sides || 12; onEdited:value=>panel.setSegment("sides",Math.round(value)) }
        UiCheck { text:"Unite overlapping segments"; enabled:!panel.topologyLocked; checked:panel.chain.unite || false; onClicked:panel.configure("unite",checked) }
        Label { text:"Radius profile · position, scale"; color:Theme.muted }
        UiField { Layout.fillWidth:true; text:(panel.chain.profile || []).join(", "); onEditingFinished:panel.configure("profile",text.split(",").map(Number)) }
    }
}
