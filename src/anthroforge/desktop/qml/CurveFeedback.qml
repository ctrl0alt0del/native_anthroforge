import QtQuick
import QtQuick.Controls

Item {
    id: feedback
    required property var viewport
    readonly property var state: authoring.curveInteraction.state
    readonly property var position: state.snap.point || state.preview.position || null
    readonly property var camera: viewport.cameraState
    readonly property point projected: {
        const refresh=camera;
        return position ? viewport.projectPoint(position[0],position[1],position[2]) : Qt.point(-100,-100);
    }
    visible: !!position
    Rectangle {
        objectName: "curveCursorMarker"
        x: feedback.projected.x-width/2; y: feedback.projected.y-height/2
        width: 15; height: 15; radius: feedback.state.snap.id ? 0 : 8
        color: "transparent"; border.width: 2
        border.color: feedback.state.snap.id ? Theme.snapColor : Theme.curvePointColor
        Rectangle { anchors.centerIn: parent; width: 3; height: 3; radius: 2; color: parent.border.color }
    }
    Label {
        x: feedback.projected.x+13; y: feedback.projected.y-24
        text: feedback.state.snap.id ? "Surface snap · "+(feedback.state.offset>=0?"+":"")+feedback.state.offset.toFixed(4)+" m" : "Click to insert point"
        color: feedback.state.snap.id ? Theme.snapColor : Theme.curvePointColor
        font.pixelSize: 11; style: Text.Outline; styleColor: "#24262b"
    }
}
