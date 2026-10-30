import AnthroForge.Desktop 1.0
import QtQuick

Item {
    id: overlay
    required property var viewport
    readonly property var tool: App.tissuePainting
    anchors.fill: parent
    function direction(x,y,z) {
        const d=viewport.cameraDirection(x,y,z);
        return [d.x,-d.z,d.y];
    }
    function camera() {
        return viewport.cameraPosition().concat(direction(1,0,0),direction(0,1,0),
            direction(0,0,-1),[viewport.pixelsPerUnit(1),!viewport.orthographic]);
    }
    Rectangle {
        visible: overlay.tool.state.active && pointer.containsMouse
        x: pointer.mouseX-width/2; y: pointer.mouseY-height/2
        width: overlay.tool.state.radius*2; height: width; radius: width/2
        color: "transparent"; border.color: overlay.tool.state.through ? "#ffb568" : "#80ccff"
        border.width: 1
    }
    MouseArea {
        id: pointer; objectName: "tissuePaintPointer"
        anchors.fill: parent; enabled: overlay.tool.state.active && !viewport.keyboard.blocked
        acceptedButtons: Qt.LeftButton; hoverEnabled: true; cursorShape: Qt.CrossCursor
        function update(mouse,press) {
            viewport.pointerPosition=Qt.point(mouse.x,mouse.y);
            overlay.tool.pointer([mouse.x-width/2,height/2-mouse.y],overlay.camera(),press);
        }
        onPressed: mouse => { viewport.forceActiveFocus(); update(mouse,true); }
        onPositionChanged: mouse => update(mouse,false)
        onReleased: mouse => { update(mouse,false); overlay.tool.release(); }
        onCanceled: overlay.tool.cancelStroke()
    }
    Connections {
        target: viewport
        function onCameraStateChanged() { if(overlay.tool.state.dragging) overlay.tool.cancelStroke(); }
        function onDistanceChanged() { if(overlay.tool.state.dragging) overlay.tool.cancelStroke(); }
    }
}
