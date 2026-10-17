import QtQuick
import QtQuick3D

Node {
    id: rig
    required property var sourceCamera
    required property bool orthographic
    readonly property var camera: orthographic ? ortho : perspective
    PerspectiveCamera {
        id: perspective
        position: rig.sourceCamera.scenePosition; rotation: rig.sourceCamera.sceneRotation
        clipNear: rig.sourceCamera.clipNear; clipFar: rig.sourceCamera.clipFar
        fieldOfView: rig.sourceCamera.fieldOfView || 60
    }
    OrthographicCamera {
        id: ortho
        position: perspective.position; rotation: perspective.rotation
        clipNear: perspective.clipNear; clipFar: perspective.clipFar
        horizontalMagnification: rig.sourceCamera.horizontalMagnification || 1
        verticalMagnification: rig.sourceCamera.verticalMagnification || 1
    }
}
