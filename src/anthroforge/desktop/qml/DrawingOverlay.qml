import QtQuick
import QtQuick.Controls

Item {
    id: overlay
    required property var viewport
    readonly property var tool: workspace.drawingTools
    readonly property bool active: tool.state.active
    anchors.fill: parent
    Canvas {
        id: stroke; anchors.fill: parent
        property var points: []
        property int painted: 0
        property bool repaintAll: true
        function reset() { points=[]; painted=0; repaintAll=true; requestPaint(); }
        function redraw() { repaintAll=true; requestPaint(); }
        onPaint: {
            const ctx=getContext("2d");
            if(repaintAll) { ctx.clearRect(0,0,width,height); painted=0; repaintAll=false; }
            ctx.strokeStyle=Theme.curveColor; ctx.lineWidth=2; ctx.beginPath();
            for(let i=Math.max(0,painted-1);i<points.length;i++) {
                const p=viewport.projectPoint(points[i][0],points[i][1],points[i][2]);
                if(i===Math.max(0,painted-1)) ctx.moveTo(p.x,p.y); else ctx.lineTo(p.x,p.y);
            }
            ctx.stroke(); painted=points.length;
        }
        Connections {
            target: overlay.tool
            function onPointsAdded(values) { for(const p of values) stroke.points.push(p); stroke.requestPaint(); }
            function onResetPreview() { stroke.reset(); }
        }
        Connections {
            target: viewport
            function onCameraStateChanged() { stroke.redraw(); overlay.tool.viewChanged(viewport.worldRay(viewport.width/2,viewport.height/2).direction); }
            function onDistanceChanged() { stroke.redraw(); }
            function onWidthChanged() { stroke.redraw(); }
            function onHeightChanged() { stroke.redraw(); }
        }
    }
    Rectangle {
        objectName: "placementPreview"
        readonly property var point: overlay.tool.state.hover
        readonly property point projected: { const camera=viewport.cameraState, distance=viewport.distance; return point.length ? viewport.projectPoint(point[0],point[1],point[2]) : Qt.point(-100,-100); }
        visible: overlay.active && point.length===3
        x: projected.x-width/2; y: projected.y-height/2
        width: overlay.tool.state.branched && overlay.tool.state.count===0 ? 14 : 8; height: width; radius: width/2
        color: Theme.curveColor; border.color: Theme.text; border.width: 2
    }
    CursorMarker { viewport: overlay.viewport }
    MouseArea {
        id: pointer
        objectName: "drawingPointer"
        anchors.fill: parent; enabled: overlay.active && !viewport.keyboard.blocked
        acceptedButtons: Qt.LeftButton; hoverEnabled: true
        cursorShape: Qt.CrossCursor
        function preview() {
            if(containsMouse && overlay.active) update({x:mouseX,y:mouseY,modifiers:viewport.keyboard.modifiers},false);
        }
        function update(mouse,press) {
            viewport.pointerPosition=Qt.point(mouse.x,mouse.y);
            const ray=viewport.worldRay(mouse.x,mouse.y), normal=viewport.worldRay(width/2,height/2).direction;
            const values=ray.origin.concat(ray.direction,[mouse.x,mouse.y,overlay.tool.state.options.radius]);
            overlay.tool.setProjection(viewport.cameraPosition(),!viewport.orthographic);
            overlay.tool.setSnapping(viewport.keyboard.matches("snapSurface",mouse.modifiers));
            if(press) overlay.tool.click(values,normal,viewport.keyboard.matches("continuePlacement",mouse.modifiers));
            else overlay.tool.pointer(values,normal,false);
        }
        onPressed: mouse => { viewport.forceActiveFocus(); update(mouse,true); }
        onPositionChanged: mouse => update(mouse,false)
        onReleased: mouse => { update(mouse,false); overlay.tool.release(); }
        onCanceled: { if(overlay.tool.state.painting) overlay.tool.clearStroke(); }
        Connections { target: viewport; function onCameraStateChanged() { pointer.preview(); } function onDistanceChanged() { pointer.preview(); } }
        Connections {
            target: viewport.keyboard
            function onModifiersChanged() { pointer.preview(); }
        }
    }
}
