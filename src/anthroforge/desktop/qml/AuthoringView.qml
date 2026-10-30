import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick3D

View3D {
    id: view
    required property var sourceCamera
    required property bool orthographic
    required property real distance
    visible: App.authoring.visible || App.tissueRegionTools.state.active
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
