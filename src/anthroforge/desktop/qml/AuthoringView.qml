import QtQuick
import QtQuick3D

View3D {
    id: view
    required property var sourceCamera
    required property bool orthographic
    required property real distance
    visible: authoring.visible || workspace.tissueRegionTools.state.active
    camera: rig.camera
    environment: SceneEnvironment {
        backgroundMode: SceneEnvironment.Transparent
        antialiasingMode: SceneEnvironment.MSAA
        antialiasingQuality: SceneEnvironment.High
    }
    PresentationCamera { id: rig; sourceCamera: view.sourceCamera; orthographic: view.orthographic }
    Node {
        eulerRotation.x: -90
        AuthoringOverlay { distance: view.distance }
        TissueRegionOverlay { distance: view.distance }
    }
}
