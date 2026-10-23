import QtQuick
import QtQuick.Controls

// Preview only while dragging; the owner commits one stable-key move on release.
Item {
    id: handle
    required property var view
    required property string key
    signal placed(string target, bool after)
    implicitWidth: 24; implicitHeight: 24
    property bool moving: false
    property real pointerY: 0
    property string target: ""
    property bool after: false
    function locate() {
        const y=Math.max(0,Math.min(view.height-1,pointerY))+view.contentY;
        const index=view.indexAt(2,y);
        const item=index>=0 ? view.itemAtIndex(index) : null;
        target=item ? item.key : "";
        after=!!item && y>item.y+item.height/2;
        view.dropKey=target; view.dropAfter=after;
    }
    function finish(commit) {
        const selected=target, below=after;
        pointer.gesture=false;
        moving=false; target=""; view.dropKey=""; focus=false;
        if(commit && selected && selected!==key) placed(selected,below);
    }
    function track(mouse) {
        pointerY=pointer.mapToItem(view,mouse.x,mouse.y).y;
        if(!moving && Math.abs(mouse.y-pointer.startY)>=Qt.styleHints.startDragDistance) {
            moving=true; forceActiveFocus();
        }
        if(moving) locate();
    }
    Keys.onEscapePressed: event => { finish(false); event.accepted=true; }
    onVisibleChanged: if(!visible) finish(false)
    Image { anchors.centerIn: parent; width: 16; height: 16; source: "icons/grip.svg"; opacity: handle.moving ? 1 : 0.7 }
    ToolTip.visible: pointer.containsMouse && !moving
    ToolTip.text: "Drag to reorder shortcuts"
    MouseArea {
        id: pointer; anchors.fill: parent; hoverEnabled: true; preventStealing: true
        acceptedButtons: Qt.LeftButton; cursorShape: Qt.SizeVerCursor
        property real startY: 0
        property bool gesture: false
        onPressed: mouse => { gesture=true; startY=mouse.y; handle.target=""; }
        onPositionChanged: mouse => { if(pressed && gesture) handle.track(mouse); }
        onReleased: handle.finish(true)
        onCanceled: handle.finish(false)
    }
    Timer {
        interval: 16; repeat: true; running: handle.moving
        onTriggered: {
            const delta=handle.pointerY<24 ? -12 : handle.pointerY>handle.view.height-24 ? 12 : 0;
            if(!delta) return;
            const view=handle.view, maximum=Math.max(0,view.contentHeight-view.height);
            view.contentY=Math.max(0,Math.min(maximum,view.contentY+delta));
            handle.locate();
        }
    }
}
