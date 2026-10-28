import QtQuick
import QtQuick3D

Repeater3D {
    required property var service
    property int side: 1
    model: service.anchors
    delegate: Repeater3D {
        required property var modelData
        model: side ? modelData.after : modelData.before
        delegate: Model {
            required property var modelData
            source: "#Sphere"; pickable: false
            position: Qt.vector3d(modelData.position[0],modelData.position[1],modelData.position[2])
            scale: Qt.vector3d(1,1,1).times(service.state.camera[5]/30000)
            materials: DefaultMaterial { diffuseColor: side ? "#f3b650" : "#62c6ed"; lighting: DefaultMaterial.NoLighting; depthDrawMode: Material.AlwaysDepthDraw }
        }
    }
}
