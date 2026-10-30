import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick3D
import AnthroForge.Native 1.0

Repeater3D {
    model: App.shortcutComparison.geometry
    delegate: Node {
        required property var item
        readonly property var geometryData: item.content
        position: Qt.vector3d(geometryData.trs[0],geometryData.trs[1],geometryData.trs[2])
        rotation: Qt.quaternion(geometryData.quaternion[0],geometryData.quaternion[1],geometryData.quaternion[2],geometryData.quaternion[3])
        scale: Qt.vector3d(geometryData.trs[6],geometryData.trs[7],geometryData.trs[8])
        Model {
            id: mesh
            objectName: "comparisonMesh_"+item.id+"_"+item.chunk
            visible: item.active && geometryData.kind === "MESH"
            pickable: false
            opacity: App.shortcutComparison.state.mode === "Overlay" ? .25 : geometryData.readonly ? .08 : 1
            geometry: MeshGeometry { assetId: geometryData.kind === "MESH" ? item.handle : 0; chunk: item.chunk; reflected: geometryData.trs[6]*geometryData.trs[7]*geometryData.trs[8] < 0 }
            materials: PrincipledMaterial { baseColor: App.shortcutComparison.state.mode === "Overlay" ? "#74d9df" : geometryData.color; roughness: .65; cullMode: Material.NoCulling }
        }
        Model {
            id: path
            objectName: "comparisonPath_"+item.id+"_"+item.chunk
            visible: item.active && geometryData.kind === "PATH"
            pickable: false
            opacity: App.shortcutComparison.state.mode === "Overlay" ? .4 : geometryData.readonly ? .12 : 1
            geometry: PathGeometry { assetId: geometryData.kind === "PATH" ? item.handle : 0; chunk: item.chunk }
            materials: DefaultMaterial { diffuseColor: "#74d9df"; lighting: DefaultMaterial.NoLighting; lineWidth: 3 }
        }
        ResourceLoader { geometries: [mesh.geometry,path.geometry] }
    }
}
