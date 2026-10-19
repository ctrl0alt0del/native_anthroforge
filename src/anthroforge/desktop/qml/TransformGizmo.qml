import QtQuick
import "GizmoGeometry.js" as Geometry
import "GizmoPaint.js" as Paint

Item {
    id: gizmo
    required property var viewport
    property var geometry: null
    property var hover: null
    property var drag: null
    property string signature: ""
    readonly property bool dragging: drag !== null
    visible: !viewport.measuring && workspace.state.handles && viewport.transformAvailable && !viewport.insertionPreview && !viewport.modalTransforming
    function refresh() {
        if (!visible) return;
        const selected=viewport.selected, q=selected.quaternion || null;
        const key=JSON.stringify([selected.trs,q,viewport.gizmoSize,viewport.toolMode,viewport.cameraState,width,height]);
        if(signature===key) return;
        signature=key;
        geometry=Geometry.geometry(viewport.projectPoint,selected.trs.slice(0,3),viewport.gizmoSize,viewport.toolMode,q);
        canvas.requestPaint();
    }
    function cancel() {
        if(drag) workspace.endTransform(true);
        drag=null; canvas.requestPaint();
        authoring.curveInteraction.clearSnap();
    }
    function begin(mouse) {
        if(!geometry || geometry.mode!==viewport.toolMode) {mouse.accepted=false;return;}
        const p=Geometry.point(mouse.x,mouse.y), hit=Geometry.hit(geometry,viewport.toolMode,p);
        if(!hit) {mouse.accepted=false;return;}
        viewport.forceActiveFocus();
        if(!workspace.beginTransform(viewport.toolMode)) return;
        const angle=hit.kind==="ring"?Geometry.rotationAngle(geometry,hit.axis,p,viewport.worldRay):null;
        drag={start:p,hit:hit,geometry:geometry,mode:viewport.toolMode,total:0,angle:angle};
    }
    function move(mouse) {
        const p=Geometry.point(mouse.x,mouse.y);
        viewport.pointerPosition=Qt.point(mouse.x,mouse.y);
        hover=Geometry.hit(geometry,geometry?geometry.mode:viewport.toolMode,p);
        updateDrag(p);
        canvas.requestPaint();
    }
    function updateDrag(p) {
        if(!drag) return;
        let values=Geometry.values(drag,p,viewport.keyboard.held("precision"),viewport.screenTranslation,viewport.worldRay);
        if(drag.mode==="Move" && authoring.active) {
            const ray=viewport.worldRay(p.x,p.y);
            values=authoring.curveInteraction.movement(ray.origin,ray.direction,values,viewport.keyboard.held("snapSurface"));
        }
        workspace.transformDelta(values);
    }
    function rebase() {
        if(!drag) return;
        signature=""; refresh();
        const p=viewport.pointerPosition, angle=drag.hit.kind==="ring"?Geometry.rotationAngle(geometry,drag.hit.axis,p,viewport.worldRay):null;
        drag={start:Geometry.point(p.x,p.y),hit:drag.hit,geometry:geometry,mode:drag.mode,total:0,angle:angle};
    }
    function probe(axis) {
        if(!geometry) return Qt.point(-100,-100);
        const p=viewport.toolMode==="Rotate"?geometry.rings[axis][12]:Geometry.along(geometry.center,geometry.axes[axis],.9);
        return mapToItem(null,p.x,p.y);
    }
    Canvas {
        id: canvas; anchors.fill: parent
        onPaint: {
            const ctx=getContext("2d");ctx.clearRect(0,0,width,height);
            if(gizmo.geometry) Paint.draw(ctx,gizmo.geometry,gizmo.geometry.mode,gizmo.drag?gizmo.drag.hit:gizmo.hover);
        }
    }
    MouseArea {
        anchors.fill: parent; acceptedButtons: Qt.LeftButton; hoverEnabled: true
        cursorShape: gizmo.hover || gizmo.drag ? Qt.SizeAllCursor : Qt.ArrowCursor
        onPressed: mouse => gizmo.begin(mouse)
        onPositionChanged: mouse => gizmo.move(mouse)
        onReleased: { if(gizmo.drag) workspace.endTransform(false); gizmo.drag=null; authoring.curveInteraction.clearSnap(); }
        onCanceled: gizmo.cancel()
        onWheel: wheel => wheel.accepted=false
        onExited: { gizmo.hover=null; canvas.requestPaint(); }
    }
    onVisibleChanged: { if(!visible) cancel(); else signature=""; }
    // Projection queries are valid after Quick 3D has synchronized the camera.
    Connections { target: gizmo.Window.window; function onFrameSwapped() { gizmo.refresh(); } }
    Connections { target: viewport; function onToolModeChanged() { gizmo.cancel(); canvas.requestPaint(); } }
    Connections { target: viewport.keyboard; function onModifiersChanged() { gizmo.updateDrag(viewport.pointerPosition); } }
}
