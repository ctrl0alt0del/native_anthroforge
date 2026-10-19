import QtQuick
import QtQuick3D

View3D {
    id: viewLayer
    required property var sourceCamera
    required property bool orthographic
    required property string depthLayer
    required property vector3d viewAxis
    visible: workspace.imageLayer(depthLayer).count > 0
    camera: rig.camera
    environment: SceneEnvironment {
        backgroundMode: SceneEnvironment.Transparent
        antialiasingMode: SceneEnvironment.MSAA
        antialiasingQuality: SceneEnvironment.High
    }
    PresentationCamera { id: rig; sourceCamera: viewLayer.sourceCamera; orthographic: viewLayer.orthographic }
    Node { eulerRotation.x: -90; ImageScene { layer: viewLayer.depthLayer; orthographic: viewLayer.orthographic; viewAxis: viewLayer.viewAxis } }
}
