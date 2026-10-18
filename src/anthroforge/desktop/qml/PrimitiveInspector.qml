import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    readonly property var item: authoring.state
    readonly property var primitive: item.primitive || {}
    readonly property var curves: item.curves || []
    readonly property var curve: curves[curveChoice.currentIndex] || {}
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
        NumericSetting { label: "Curve evaluation resolution"; value: panel.curve.resolution || 24; decimals: 0; enabled: !panel.topologyLocked; onEdited: value => panel.curveSetting("resolution",Math.round(value)) }
        UiCheck { visible: panel.primitive.kind === "LOFT"; text: "Override sampling range"; checked: panel.curve.start !== null && panel.curve.start !== undefined; onClicked: { panel.curveSetting("start",checked?0:null); panel.curveSetting("span",checked?1:null); } }
        NumericSetting { visible: panel.primitive.kind === "LOFT" && panel.curve.start !== null; label: "Curve start"; value: panel.curve.start || 0; onEdited: value => panel.curveSetting("start",value) }
        NumericSetting { visible: panel.primitive.kind === "LOFT" && panel.curve.span !== null; label: "Curve span"; value: panel.curve.span || 1; onEdited: value => panel.curveSetting("span",value) }
        Label { text: "Control point"; color: Theme.muted }
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
