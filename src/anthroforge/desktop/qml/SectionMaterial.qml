import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick3D

CustomMaterial {
    property color tint: "white"
    property bool vertexColor: false
    property bool unlit: false
    property var equation: App.sectionTools.state.plane
    property vector3d clipNormal: Qt.vector3d(equation[0],equation[2],-equation[1])
    property real clipOffset: equation[3]
    cullMode: Material.NoCulling
    shadingMode: CustomMaterial.Shaded
    fragmentShader: "shaders/section.frag"
}
