import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    readonly property var item: authoring.state
    readonly property var primitive: item.primitive || {}
    readonly property var curves: item.curves || []
    readonly property var curve: curves[curveChoice.currentIndex] || {}
    readonly property var use: (item.uses || []).find(u => u.curve === curve.id) || {}
    readonly property var points: curve.points || []
    readonly property var point: points[pointChoice.currentIndex] || {}
    readonly property var piece: (primitive.pieces || []).find(p => p.curve === curve.id) || {}
    readonly property bool topologyLocked: (item.topology_dependents || []).length > 0
    Layout.fillWidth: true; spacing: 8
    function primitiveSetting(key,value) { authoring.setting("primitive.update",key,value); }
    function curveSetting(key,value) { const args={entity:item.id,curve:curve.id}; args[key]=value; authoring.edit("curve.update",args); }
    function pointSetting(key,value) { const args={entity:item.id,curve:curve.id,point:point.id}; args[key]=value; authoring.edit("point.update",args); }
    function pieceSetting(key,value) { const args={entity:item.id,piece:piece.id}; args[key]=value; authoring.edit("body.update",args); }
    function syncSelection() {
        const selected=authoring.selectedComponent;
        if(!selected.curve || !selected.point) return;
        const curveIndex=panel.curves.findIndex(c=>c.id===selected.curve);
        if(curveIndex<0) return;
        curveChoice.currentIndex=curveIndex;
        pointChoice.currentIndex=panel.curves[curveIndex].points.findIndex(p=>p.id===selected.point);
    }
    Connections { target: authoring; function onChanged() { panel.syncSelection(); } }
    UiSection {
        title: panel.item.standalone ? "Curve" : "Primitive"
        Label { text: panel.item.standalone ? (panel.curve.engine || "Curve") : panel.primitive.kind === "LOFT" ? "Ordered curve loft" : panel.primitive.kind === "BODY" ? "Curve-deformed body" : "Imported mesh"; color: Theme.text }
        UiButton { objectName: "editPrimitive"; text: panel.item.editing ? "Finish editing" : panel.item.standalone ? "Edit Curve" : "Edit Primitive"; checkable: true; checked: panel.item.editing || false; Layout.fillWidth: true; onClicked: authoring.setEditing(!panel.item.editing) }
        UiCombo { visible: panel.item.editing && panel.primitive.kind === "BODY"; Layout.fillWidth: true; model: ["Curve controls", "Base vertices · Hook assignment"]; currentIndex: panel.item.category === "BASE" ? 1 : 0; onActivated: authoring.setCategory(currentIndex === 1 ? "BASE" : "CURVE") }
        Label { visible: panel.topologyLocked; text: "Topology locked by child or surface attachments"; color: Theme.accent; wrapMode: Text.WordWrap; Layout.fillWidth: true }
        NumericSetting { objectName: "primitiveSamples"; visible: !panel.item.standalone && panel.primitive.kind !== "IMPORTED"; label: "Samples"; value: panel.primitive.samples || 32; decimals: 0; enabled: !panel.topologyLocked; onEdited: value => panel.primitiveSetting("samples",Math.round(value)) }
        NumericSetting { visible: panel.primitive.kind === "LOFT"; label: "Across each strip"; value: panel.primitive.strips || 1; decimals: 0; enabled: !panel.topologyLocked; onEdited: value => panel.primitiveSetting("strips",Math.round(value)) }
        NumericSetting { visible: panel.primitive.kind === "LOFT"; label: "Sampling start"; value: panel.primitive.start || 0; onEdited: value => panel.primitiveSetting("start",value) }
        NumericSetting { visible: panel.primitive.kind === "LOFT"; label: "Sampling span"; value: panel.primitive.span || 1; onEdited: value => panel.primitiveSetting("span",value) }
        UiCheck { visible: panel.primitive.kind === "LOFT"; text: "Cap closed cross-sections"; checked: panel.primitive.caps || false; enabled: !panel.topologyLocked; onClicked: panel.primitiveSetting("caps",checked) }
        Label { text: panel.item.result && panel.item.result.status === "pending" ? "Pending changes · last accepted geometry shown" : ""; visible: !!text; color: Theme.accent; Layout.fillWidth: true; wrapMode: Text.WordWrap }
        Label { text: "Using accepted support · upstream changes pending"; visible: !!panel.item.result && (panel.item.result.pending || []).length>0; color: Theme.accent; Layout.fillWidth: true; wrapMode: Text.WordWrap }
        UiButton { text: panel.item.standalone ? "Recalculate curve" : "Recalculate this SCP"; Layout.fillWidth: true; onClicked: workspace.run("evaluate",{entities:[panel.item.id]}) }
    }
    UiSection {
        title: "Curves"; visible: panel.item.editing && panel.curves.length > 0
        UiCombo { id: curveChoice; objectName: "curveChoice"; Layout.fillWidth: true; model: panel.curves; textRole: "name" }
        ColumnLayout {
            visible: !panel.item.standalone; Layout.fillWidth: true
            UiCombo { Layout.fillWidth: true; model: ["Shape and transform","Shape only"]; currentIndex: panel.use.mode === "SHAPE_ONLY" ? 1 : 0; hint: "Switching preserves current placement"; onActivated: workspace.run("primitive.curve_mode",{entity:panel.item.id,curve:panel.curve.id,mode:currentIndex===1?"SHAPE_ONLY":"SHAPE_AND_TRANSFORM"}) }
            UiCheck { text: "Reverse direction"; checked: panel.use.reverse || false; onClicked: workspace.run("primitive.curve_reverse",{entity:panel.item.id,curve:panel.curve.id,enabled:checked}) }
            UiCheck { objectName:"curveSampleOverride"; text:"Override sample count"; enabled:!panel.topologyLocked; checked:panel.use.samples!==null && panel.use.samples!==undefined; onClicked:workspace.run("consumer.sampling",{entity:panel.item.id,curve:panel.curve.id,samples:checked ? panel.primitive.samples : null}) }
            NumericSetting { objectName:"curveSamples"; visible:!!panel.use.samples; label:panel.primitive.kind==="LOFT" ? "Minimum loft samples" : "Curve samples"; decimals:0; value:panel.use.samples || 32; enabled:!panel.topologyLocked; onEdited:value=>workspace.run("consumer.sampling",{entity:panel.item.id,curve:panel.curve.id,samples:Math.round(value)}) }
            Label { Layout.fillWidth: true; wrapMode: Text.WordWrap; color: Theme.muted; text: "Used by: "+(panel.use.users || []).map(u=>u.name).join(", ") }
            RowLayout {
                UiButton { text: "Select source"; onClicked: workspace.select(panel.curve.id) }
                UiButton { text: "Make independent"; hint: "Copy this consumer's source with new identities"; onClicked: workspace.run("primitive.make_independent",{entity:panel.item.id,curve:panel.curve.id}) }
            }
        }
        RowLayout {
            visible: !panel.item.standalone
            UiButton { text: "Add"; enabled: !panel.topologyLocked; onClicked: authoring.edit("curve.add",{entity:panel.item.id}) }
            UiButton { text: "Copy"; enabled: !panel.topologyLocked; onClicked: authoring.edit("curve.add",{entity:panel.item.id,source:panel.curve.id}) }
            UiButton { text: "Remove"; enabled: !panel.topologyLocked; onClicked: authoring.edit("curve.remove",{entity:panel.item.id,curve:panel.curve.id}) }
        }
        RowLayout {
            visible: !panel.item.standalone
            Repeater {
                model: [-1,1]
                UiButton { required property int modelData; text: modelData<0 ? "Earlier" : "Later"; enabled: !panel.topologyLocked && curveChoice.currentIndex+modelData>=0 && curveChoice.currentIndex+modelData<panel.curves.length
                    onClicked: { const ids=panel.curves.map(c=>c.id), i=curveChoice.currentIndex, j=i+modelData; [ids[i],ids[j]]=[ids[j],ids[i]]; authoring.edit("curve.order",{entity:panel.item.id,curves:ids}); curveChoice.currentIndex=j; } }
            }
        }
        UiCheck { text: "Closed curve"; checked: panel.curve.closed || false; enabled: !panel.topologyLocked; onClicked: panel.curveSetting("closed",checked) }
        NumericSetting { visible: panel.curve.engine === "BEZIER"; label: "Curve evaluation resolution"; value: panel.curve.resolution || 24; decimals: 0; enabled: !panel.topologyLocked; onEdited: value => panel.curveSetting("resolution",Math.round(value)) }
        CurveConversion { id: conversion; curve: panel.curve; enabled: !panel.topologyLocked }
        RoutingSettings { curve: panel.curve; topologyLocked: panel.topologyLocked; converting: conversion.expanded }
        FiberCreation { curve: panel.curve }
        UiCheck { visible: panel.primitive.kind === "LOFT"; text: "Override sampling range"; checked: panel.curve.start !== null && panel.curve.start !== undefined; onClicked: { panel.curveSetting("start",checked?0:null); panel.curveSetting("span",checked?1:null); } }
        NumericSetting { visible: panel.primitive.kind === "LOFT" && panel.curve.start !== null; label: "Curve start"; value: panel.curve.start || 0; onEdited: value => panel.curveSetting("start",value) }
        NumericSetting { visible: panel.primitive.kind === "LOFT" && panel.curve.span !== null; label: "Curve span"; value: panel.curve.span || 1; onEdited: value => panel.curveSetting("span",value) }
        Label { text: "Control point"; color: Theme.muted }
        FiberBinding { curve: panel.curve; point: panel.point }
        CurveJunction { curve: panel.curve; point: panel.point }
        UiCombo { id: pointChoice; objectName: "pointChoice"; Layout.fillWidth: true; model: panel.points.map((p,i)=>"Point "+(i+1)); onActivated: { const rows=authoring.componentRows.filter(r=>r.point===panel.point.id && r.part==="position"); if(rows.length) authoring.selectComponent(rows[0].key,false); } }
        VectorSetting { length: true; label: "Point position"; values: panel.point.position || [0,0,0]; onEdited: values => panel.pointSetting("position",values) }
        Repeater {
            model: ["left","right"]
            ColumnLayout {
                required property string modelData
                visible: panel.curve.engine === "BEZIER"
                Layout.fillWidth: true
                UiCombo { Layout.fillWidth: true; model: ["AUTO","ALIGNED","FREE","VECTOR"]; currentIndex: Math.max(0,model.indexOf(panel.point[modelData+"_mode"])); onActivated: panel.pointSetting(modelData+"_mode",currentText) }
                VectorSetting { length: true; label: modelData === "left" ? "Left handle" : "Right handle"; values: panel.point[modelData] || [0,0,0]; enabled: panel.point[modelData+"_mode"] === "FREE" || panel.point[modelData+"_mode"] === "ALIGNED"; onEdited: values => panel.pointSetting(modelData,values) }
            }
        }
        NumericSetting { label: "Radius"; value: panel.point.radius === undefined ? 1 : panel.point.radius; onEdited: value => panel.pointSetting("radius",value) }
        NumericSetting { label: "Tilt · radians"; value: panel.point.tilt || 0; onEdited: value => panel.pointSetting("tilt",value) }
        UiCheck { objectName: "pointStackingFixed"; text: "Keep fixed during stacking"; checked: panel.point.stacking_fixed || false; hint: "Retain this material location in surfaces built from this curve"; onClicked: panel.pointSetting("stacking_fixed",checked) }
        UiCheck { objectName: "pointProtectedCrease"; text: "Protect crease"; checked: panel.point.protected_crease || false; hint: "Retain this structural point during tissue stacking"; onClicked: panel.pointSetting("protected_crease",checked) }
        RowLayout {
            UiButton { text: "Insert point"; onClicked: { const p=(panel.point.position || [0,0,0]).slice(); p[0]+=.1; authoring.edit("point.insert",{entity:panel.item.id,curve:panel.curve.id,index:pointChoice.currentIndex+1,point:{position:p}}); } }
            UiButton { text: "Remove point"; enabled: panel.points.length>(panel.curve.closed?3:2); onClicked: authoring.edit("point.remove",{entity:panel.item.id,curve:panel.curve.id,point:panel.point.id}) }
        }
    }
    UiSection {
        title: "Body piece"; visible: panel.item.editing && !!panel.piece.id
        UiCombo { Layout.fillWidth: true; model: ["BOX","CYLINDER","CAPSULE"]; currentIndex: Math.max(0,model.indexOf(panel.piece.shape)); enabled: !panel.topologyLocked; onActivated: panel.pieceSetting("shape",currentText) }
        NumericSetting { length: true; label: "Width"; value: panel.piece.width || .1; onEdited: value => panel.pieceSetting("width",value) }
        NumericSetting { length: true; label: "Depth"; value: panel.piece.depth || .1; onEdited: value => panel.pieceSetting("depth",value) }
        UiCheck { text: "Fit entire curve"; checked: panel.piece.fit === undefined || panel.piece.fit; onClicked: panel.pieceSetting("fit",checked) }
        NumericSetting { length: true; label: "Fixed length"; value: panel.piece.length || 1; enabled: !panel.piece.fit; onEdited: value => panel.pieceSetting("length",value) }
        NumericSetting { length: true; label: "Position along curve"; value: panel.piece.position || 0; onEdited: value => panel.pieceSetting("position",value) }
        NumericSetting { label: "Radial sides"; value: panel.piece.sides || 16; decimals: 0; enabled: !panel.topologyLocked; onEdited: value => panel.pieceSetting("sides",Math.round(value)) }
    }
    DeformerStack { visible: !panel.item.standalone; item: panel.item }
    ThicknessInspector { visible: !panel.item.standalone; item: panel.item; topologyLocked: panel.topologyLocked }
}
