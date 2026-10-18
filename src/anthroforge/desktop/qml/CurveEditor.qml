import QtQuick

Item {
    id: editor
    required property var viewport
    required property var keyboard
    readonly property var interaction: authoring.curveInteraction
    readonly property bool dragging: drag !== null
    readonly property bool previewActive: visible && !workspace.state.hidden_categories.includes("curves") && !workspace.state.unpickable_categories.includes("curves") && keyboard.held("insertPoint") &&
        !viewport.transforming && !viewport.navigating && viewport.pointerPosition.x >= 0
    property var pending: null
    property var drag: null
    property string signature: ""
    visible: !viewport.measuring && authoring.visible && authoring.state.editing && authoring.state.category === "CURVE" &&
        !!authoring.state.curves?.length && !workspace.selectedData.readonly && !keyboard.blocked
    function refreshPreview() {
        if(!previewActive) { interaction.clearPreview(); signature=""; return; }
        const p=viewport.pointerPosition, key=JSON.stringify([p,viewport.cameraState,viewport.distance,width,height,workspace.state.revision]);
        if(key===signature) return;
        signature=key;
        const ray=viewport.worldRay(p.x,p.y);
        interaction.updatePreview(ray.origin,ray.direction);
    }
    function press(mouse) {
        viewport.forceActiveFocus(); viewport.pointerPosition=Qt.point(mouse.x,mouse.y);
        if(previewActive) { signature=""; refreshPreview(); interaction.insert(); signature=""; return; }
        if(keyboard.matches("deeperSelection",mouse.modifiers)) { mouse.accepted=false; return; }
        const ray=viewport.worldRay(mouse.x,mouse.y), extend=keyboard.matches("extendSelection",mouse.modifiers);
        const hit=interaction.pressPoint(ray.origin,ray.direction,viewport.distance*.012,extend);
        if(!hit.key) { mouse.accepted=false; return; }
        pending={x:mouse.x,y:mouse.y,pivot:hit.position,extend:extend};
    }
    function move(mouse) {
        viewport.pointerPosition=Qt.point(mouse.x,mouse.y);
        if(pending && Math.hypot(mouse.x-pending.x,mouse.y-pending.y)>=4) {
            interaction.beginPointDrag(pending.extend);
            if(workspace.beginTransform("Move")) drag=pending;
            pending=null;
        }
        updateDrag();
    }
    function updateDrag() {
        if(!drag) return;
        const p=viewport.pointerPosition, ray=viewport.worldRay(p.x,p.y);
        const delta=viewport.screenTranslationAt({x:p.x-drag.x,y:p.y-drag.y},drag.pivot);
        const values=interaction.movement(ray.origin,ray.direction,delta.concat([0,0,0,1,1,1]),keyboard.held("snapSurface"));
        workspace.transformDelta(values);
    }
    function finish(cancel) {
        if(drag) workspace.endTransform(cancel);
        else if(pending && !cancel) interaction.clickPoint(pending.extend);
        drag=null; pending=null; interaction.clearSnap(); signature="";
    }
    function rebase() {
        if(!drag) return;
        const p=viewport.pointerPosition;
        drag={x:p.x,y:p.y,pivot:authoring.transformData.trs.slice(0,3),extend:drag.extend};
    }
    onPreviewActiveChanged: refreshPreview()
    onVisibleChanged: { if(!visible) { finish(true); interaction.clearPreview(); } }
    MouseArea {
        anchors.fill: parent; acceptedButtons: Qt.LeftButton; hoverEnabled: true
        cursorShape: editor.previewActive ? Qt.CrossCursor : editor.dragging ? Qt.SizeAllCursor : Qt.ArrowCursor
        onPressed: mouse => editor.press(mouse)
        onPositionChanged: mouse => editor.move(mouse)
        onReleased: editor.finish(false)
        onCanceled: editor.finish(true)
        onExited: { if(!viewport.transforming) viewport.pointerPosition=Qt.point(-1,-1); }
        onWheel: wheel => wheel.accepted=false
    }
    Timer { interval: 25; repeat: true; running: editor.previewActive; onTriggered: editor.refreshPreview() }
    Connections { target: keyboard; function onModifiersChanged() { editor.updateDrag(); } }
    Connections { target: authoring; function onGeometryChanged() { editor.signature=""; } }
}
