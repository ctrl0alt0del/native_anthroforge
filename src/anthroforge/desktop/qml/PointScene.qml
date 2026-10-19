import QtQuick
import QtQuick3D

Repeater3D {
    required property real markerScale
    model: workspace.constructionModel
    delegate: Model {
        required property var item
        readonly property var location: item.world_position || [0,0,0]
        objectName: "constructionPoint_" + item.id
        visible: !!item.world_position && item.visible
        position: Qt.vector3d(location[0], location[1], location[2])
        source: "#Sphere"
        scale: Qt.vector3d(markerScale, markerScale, markerScale)
        opacity: item.readonly ? 0.12 : 1.0
        materials: DefaultMaterial {
            lighting: DefaultMaterial.NoLighting
            diffuseColor: item.id === workspace.selectedId ? "#ffffff" : item.color
        }
    }
}
