import QtQuick
import QtQuick3D
import AnthroForge.Native 1.0

Repeater3D {
    id: meshes
    required property var effects
    model: workspace.meshModel
    delegate: Node {
        required property var item
        position: Qt.vector3d(item.trs[0],item.trs[1],item.trs[2])
        rotation: Qt.quaternion(item.quaternion[0],item.quaternion[1],item.quaternion[2],item.quaternion[3])
        scale: Qt.vector3d(item.trs[6],item.trs[7],item.trs[8])
        Model {
            id: mask
            objectName: "shortcutMask_"+item.key
            visible: item.active && !(workspace.tissueInspection.state.hiddenOwners || []).includes(item.id)
            position: Qt.vector3d(item.geometry_offset[0],item.geometry_offset[1],item.geometry_offset[2])
            geometry: MeshGeometry { assetId: item.handle; chunk: item.chunk }
            property color tint: meshes.effects.colors?.[item.id] || "black"
            property Material normalMaterial: DefaultMaterial { lighting: DefaultMaterial.NoLighting; diffuseColor: mask.tint; cullMode: Material.NoCulling }
            property Material clippedMaterial: SectionMaterial { tint: mask.tint; unlit: true }
            materials: workspace.sectionTools.state.enabled && workspace.sectionTools.state.cut && workspace.sectionTools.state.wholeScene ? clippedMaterial : normalMaterial
        }
    }
}
