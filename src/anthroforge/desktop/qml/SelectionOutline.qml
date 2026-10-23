import QtQuick
import QtQuick3D

Item {
    id: outline
    required property var sourceCamera
    property bool orthographic: false
    property real useMaskColors: 0
    property Component content
    property alias sceneRoot: maskRoot
    View3D {
        id: maskView; anchors.fill: parent
        camera: rig.camera
        environment: SceneEnvironment {
            backgroundMode: SceneEnvironment.Color; clearColor: "black"
            antialiasingMode: SceneEnvironment.MSAA; antialiasingQuality: SceneEnvironment.High
        }
        PresentationCamera { id: rig; sourceCamera: outline.sourceCamera; orthographic: outline.orthographic }
        Node {
            id: maskRoot; eulerRotation.x: -90
            Loader3D { active: outline.visible; sourceComponent: outline.content }
        }
    }
    ShaderEffectSource {
        id: maskTexture; sourceItem: maskView; hideSource: true; live: outline.visible
        visible: false; textureSize: Qt.size(outline.width, outline.height)
    }
    ShaderEffect {
        anchors.fill: parent
        property var source: maskTexture
        property vector2d texel: Qt.vector2d(1/Math.max(1,width), 1/Math.max(1,height))
        property real useMaskColors: outline.useMaskColors
        fragmentShader: "qrc:/anthroforge/shaders/outline.frag.qsb"
    }
}
