import QtQuick
import QtQuick3D
import QtQuick.Controls

Item {
    id: panel
    required property var service
    property int side: 1
    property bool overlay: false
    readonly property var cameraState: service.state.camera
    View3D {
        id: view; anchors.fill: parent; camera: camera
        environment: SceneEnvironment { clearColor: "#25282d"; backgroundMode: SceneEnvironment.Color; antialiasingMode: SceneEnvironment.MSAA }
        Node {
            position: Qt.vector3d(panel.cameraState[0],panel.cameraState[2],-panel.cameraState[1])
            eulerRotation: Qt.vector3d(panel.cameraState[3],panel.cameraState[4],0)
            PerspectiveCamera { id: camera; z: panel.cameraState[5]; clipNear: Math.max(.00001,z/10000); clipFar: z*100; fieldOfView: 45 }
            DirectionalLight { eulerRotation: Qt.vector3d(-30,-25,0); brightness: 1.1 }
        }
        DirectionalLight { eulerRotation: Qt.vector3d(30,130,0); brightness: .6 }
        Node {
            eulerRotation.x: -90
            SkeletonSceneGeometry { service: panel.service; model: panel.side ? panel.service.after : panel.service.before }
            SkeletonSceneGeometry { service: panel.service; model: panel.overlay ? panel.service.before : null; overlay: true }
            SkeletonAnchors { service: panel.service; side: panel.side }
            SkeletonAnchors { service: panel.service; side: 0; visible: panel.overlay }
        }
    }
    Label { anchors.left: parent.left; anchors.top: parent.top; anchors.margins: 10; text: panel.overlay ? "Overlay" : panel.side ? "After" : "Before"; color: Theme.text; font.bold: true }
    MouseArea {
        anchors.fill: parent; acceptedButtons: Qt.LeftButton | Qt.MiddleButton | Qt.RightButton
        property point start
        property bool moved: false
        onPressed: mouse=>{ start=Qt.point(mouse.x,mouse.y); moved=false; }
        onPositionChanged: mouse=>{ if(pressed) { const dx=mouse.x-start.x,dy=mouse.y-start.y; if(Math.abs(dx)+Math.abs(dy)>1) moved=true; panel.service.orbit(dx,dy); start=Qt.point(mouse.x,mouse.y); } }
        onWheel: wheel=>panel.service.zoom(wheel.angleDelta.y)
        onReleased: mouse=>{
            if(moved || mouse.button!==Qt.LeftButton) return;
            const f=2*Math.tan(camera.fieldOfView*Math.PI/360)/height;
            const o=camera.mapPositionToScene(Qt.vector3d(0,0,0));
            const d=camera.mapDirectionToScene(Qt.vector3d((mouse.x-width/2)*f,(height/2-mouse.y)*f,-1));
            panel.service.pick(panel.side,[o.x,-o.z,o.y],[d.x,-d.z,d.y],f*camera.z*6);
        }
        onDoubleClicked: panel.service.focus("")
    }
}
