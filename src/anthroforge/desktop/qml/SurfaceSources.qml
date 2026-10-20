import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiSection {
    id: panel
    required property var item
    readonly property var uses: item.uses || []
    readonly property var use: uses[choice.currentIndex] || {}
    readonly property bool branched: !!item.branches?.length
    readonly property var available: {
        const revision=workspace.state.revision;
        return expanded && item.id ? workspace.surfaceOptions(item.id,"").sources || [] : [];
    }
    title: "Source curves"
    function update(key,value) { const args={target:item.id,curve:use.curve}; args[key]=value; workspace.run("surface.source",args); }
    function move(step) {
        const ids=uses.map(u=>u.curve), index=choice.currentIndex, other=index+step;
        if(other<0 || other>=ids.length) return;
        [ids[index],ids[other]]=[ids[other],ids[index]];
        workspace.run("surface.order",{target:item.id,curves:ids}); choice.currentIndex=other;
    }
    UiCombo { id: choice; objectName:"surfaceSourceChoice"; Layout.fillWidth:true; model:panel.uses; textRole:"name"; hint:"Source to inspect" }
    RowLayout {
        Layout.fillWidth: true
        UiButton { objectName:"editSurfaceSource"; Layout.fillWidth:true; text:"Edit curve"; enabled:!!panel.use.curve; onClicked:workspace.editConstruction(panel.use.curve) }
        UiButton { text:"↑"; enabled:!panel.branched && choice.currentIndex>0; onClicked:panel.move(-1) }
        UiButton { text:"↓"; enabled:!panel.branched && choice.currentIndex+1<panel.uses.length; onClicked:panel.move(1) }
        UiButton { objectName:"surfaceRemoveSource"; text:"Remove"; enabled:!panel.branched && panel.item.kind!=="PATCH" && panel.uses.length>2; onClicked:workspace.run("surface.source.remove",{target:panel.item.id,curve:panel.use.curve}) }
    }
    UiCombo { Layout.fillWidth:true; model:["Shape and transform","Shape only"]; currentIndex:panel.use.mode==="SHAPE_ONLY"?1:0; onActivated:panel.update("mode",currentIndex===1?"SHAPE_ONLY":"SHAPE_AND_TRANSFORM") }
    UiCheck { text:"Reverse direction"; checked:panel.use.reverse || false; onClicked:panel.update("reverse",checked) }
    UiButton {
        objectName:"surfaceIndependent"+choice.currentIndex
        enabled:!!panel.use.curve
        text:panel.branched?"Make assembly independent":"Make Independent"
        hint:panel.branched?"Copy connected sources together to preserve their junctions":"Copy this source with independent authored identities"
        onClicked:workspace.run("consumer.make_independent",{entity:panel.item.id,curve:panel.use.curve})
    }
    NumericSetting { label:"Uniform samples"; value:panel.use.samples || 32; decimals:0; enabled:!panel.item.exact; onEdited:value=>panel.update("samples",Math.round(value)) }
    NumericSetting { label:"Start fraction"; value:panel.use.start || 0; onEdited:value=>panel.update("start",value) }
    NumericSetting { label:"Span fraction"; value:panel.use.span ?? 1; onEdited:value=>panel.update("span",value) }
    RowLayout {
        visible:!panel.branched; Layout.fillWidth:true
        UiCombo { id:addition; objectName:"surfaceNewSource"; Layout.fillWidth:true; model:panel.available; textRole:"name"; valueRole:"id"; hint:"Available source curve" }
        UiButton {
            objectName:"surfaceAddSource"; text:panel.item.kind==="PATCH"?"Replace":"Add"; enabled:!!addition.currentValue
            onClicked: {
                if(panel.item.kind==="PATCH") workspace.run("surface.sources",{target:panel.item.id,curves:[addition.currentValue]});
                else workspace.run("surface.source.add",{target:panel.item.id,curve:addition.currentValue});
            }
        }
    }
}
