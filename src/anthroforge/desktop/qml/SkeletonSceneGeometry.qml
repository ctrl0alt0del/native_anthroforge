import QtQuick
import QtQuick3D
import AnthroForge.Native 1.0

Repeater3D {
    required property var service
    property bool overlay: false
    delegate: Node {
        required property var item
        readonly property var geometryData: item.content
        position: Qt.vector3d(geometryData.trs[0],geometryData.trs[1],geometryData.trs[2])
        rotation: Qt.quaternion(geometryData.quaternion[0],geometryData.quaternion[1],geometryData.quaternion[2],geometryData.quaternion[3])
        scale: Qt.vector3d(geometryData.trs[6],geometryData.trs[7],geometryData.trs[8])
        Model {
            id: mesh
            visible: item.active && geometryData.kind === "MESH"
            pickable: false; opacity: overlay ? .25 : 1
            geometry: MeshGeometry { assetId: geometryData.kind === "MESH" ? item.handle : 0; chunk: item.chunk; reflected: geometryData.trs[6]*geometryData.trs[7]*geometryData.trs[8] < 0 }
            materials: PrincipledMaterial {
                baseColor: item.id === service.state.selection ? Theme.accent : overlay ? "#72b8ad" : geometryData.color
                roughness: .65; cullMode: Material.NoCulling
            }
        }
        Model {
            id: path
            visible: item.active && geometryData.kind === "PATH"; pickable: false
            geometry: PathGeometry { assetId: geometryData.kind === "PATH" ? item.handle : 0; chunk: item.chunk }
            materials: DefaultMaterial { diffuseColor: "#b996cc"; lighting: DefaultMaterial.NoLighting; lineWidth: 2 }
        }
        ResourceLoader { geometries: [mesh.geometry,path.geometry] }
    }
}
