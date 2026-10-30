import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls

Item {
    id: modal
    required property var viewport
    property var gesture: null
    readonly property bool active: gesture !== null
    visible: active
    function begin(mode) {
        if(viewport.keyboard.blocked || !viewport.transformAvailable) return;
        if(!active && viewport.transforming) return;
        if(active) App.viewport.rebaseTransform(mode);
        else if(!App.viewport.beginTransform(mode)) return;
        viewport.forceActiveFocus();
        gesture={mode:mode}; rebase();
    }
    function rebase() {
        if(!active) return;
        const p=viewport.pointerPosition, pivot=viewport.selected.trs.slice(0,3);
        const center=viewport.projectPoint(...pivot), ray=viewport.worldRay(viewport.width/2,viewport.height/2);
        const dx=p.x-center.x, dy=center.y-p.y;
        gesture={mode:gesture.mode,start:Qt.point(p.x,p.y),pivot:pivot,center:center,total:0,
            angle:Math.atan2(dy,dx),radius:Math.hypot(dx,dy),axis:ray.direction.map(n=>-n)};
    }
    function update() {
        if(!active) return;
        const p=viewport.pointerPosition, g=gesture, factor=viewport.keyboard.held("precision") ? 0.1 : 1;
        let values=[0,0,0,0,0,0,1,1,1];
        if(g.mode==="Move") values=moveValues(p,factor);
        else if(g.mode==="Rotate") values=rotationValues(p,factor);
        else {
            const radius=Math.hypot(p.x-g.center.x,p.y-g.center.y);
            const amount=g.radius>12?(radius/g.radius-1):((p.x-g.start.x)-(p.y-g.start.y))/120;
            const scale=Math.max(.01,1+amount*factor); values=[0,0,0,0,0,0,scale,scale,scale];
        }
        App.viewport.transformDelta(values);
    }
    function moveValues(p,factor) {
        const g=gesture, ray=viewport.worldRay(p.x,p.y);
        const shift=viewport.screenTranslationAt({x:p.x-g.start.x,y:p.y-g.start.y},g.pivot).map(n=>n*factor);
        return App.authoring.curveInteraction.movement(ray.origin,ray.direction,shift.concat([0,0,0,1,1,1]),viewport.keyboard.held("snapSurface"));
    }
    function rotationValues(p,factor) {
        const g=gesture, angle=Math.atan2(g.center.y-p.y,p.x-g.center.x);
        g.total+=Math.atan2(Math.sin(angle-g.angle),Math.cos(angle-g.angle)); g.angle=angle;
        return App.viewport.rotationDelta(g.axis,g.total*180/Math.PI*factor);
    }
    function finish(cancel) {
        if(!active) return;
        gesture=null; App.viewport.endTransform(cancel); App.authoring.curveInteraction.clearSnap();
    }
    MouseArea {
        anchors.fill: parent; hoverEnabled: true; acceptedButtons: Qt.LeftButton | Qt.RightButton
        cursorShape: Qt.SizeAllCursor
        onPositionChanged: mouse => { viewport.pointerPosition=Qt.point(mouse.x,mouse.y); modal.update(); }
        onPressed: mouse => modal.finish(mouse.button===Qt.RightButton)
        onWheel: wheel => wheel.accepted=false
    }
    Label {
        anchors.horizontalCenter: parent.horizontalCenter; y: 55
        text: modal.active ? modal.gesture.mode+" · Left click / Enter: confirm · Right click / Esc: cancel\n"+
            ["viewX","viewY","viewZ"].map(command => viewport.keyboard.shortcut(command)).join(" / ")+": axis view · "+viewport.keyboard.shortcut("restoreView")+": restore view" : ""
        horizontalAlignment: Text.AlignHCenter
        color: Theme.accent; style: Text.Outline; styleColor: "#24262b"
    }
    Connections { target: viewport.keyboard; function onModifiersChanged() { modal.update(); } }
}
