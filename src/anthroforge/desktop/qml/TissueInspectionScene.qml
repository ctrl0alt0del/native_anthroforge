import QtQuick
import QtQuick3D
import AnthroForge.Native 1.0

Node {
    id: root
    required property real distance
    ViewSnapshot { id: evidence; source: workspace.tissueInspection }
    ViewSnapshot { id: section; source: workspace.sectionTools }
    Repeater3D {
        model: workspace.tissueInspection.geometry
        delegate: Node {
            id: stageNode
            required property var item
            readonly property var geometryData: item.content
            readonly property bool clipped: section.data.enabled && section.data.cut && (section.data.wholeScene || item.owner===section.data.target)
            position: Qt.vector3d(stageNode.geometryData.trs[0],stageNode.geometryData.trs[1],stageNode.geometryData.trs[2])
            rotation: Qt.quaternion(stageNode.geometryData.quaternion[0],stageNode.geometryData.quaternion[1],stageNode.geometryData.quaternion[2],stageNode.geometryData.quaternion[3])
            scale: Qt.vector3d(stageNode.geometryData.trs[6],stageNode.geometryData.trs[7],stageNode.geometryData.trs[8])
            Model {
                id: surface
                objectName: "inspectionSurface_"+stageNode.geometryData.stage+"_"+item.chunk
                visible: item.active && stageNode.geometryData.kind==="MESH"
                geometry: MeshGeometry { assetId: stageNode.geometryData.kind==="MESH" ? item.handle : 0; chunk: item.chunk; reflected: stageNode.geometryData.trs[6]*stageNode.geometryData.trs[7]*stageNode.geometryData.trs[8] < 0 }
                opacity: item.reference ? .3 : evidence.data.reference && evidence.data.mode==="Overlay" ? .7 : 1
                property Material original: PrincipledMaterial { baseColor: item.color; roughness: .65; cullMode: Material.NoCulling }
                property Material cut: SectionMaterial { tint: item.color }
                materials: stageNode.clipped ? cut : original
            }
            Model {
                id: heat
                objectName: "inspectionHeat_"+item.chunk
                visible: item.active && stageNode.geometryData.kind==="HEAT"
                geometry: InspectionGeometry { assetId: stageNode.geometryData.kind==="HEAT" ? item.handle : 0; chunk: item.chunk }
                property Material original: PrincipledMaterial { baseColor: "white"; vertexColorsEnabled: true; roughness: .8; cullMode: Material.NoCulling }
                property Material cut: SectionMaterial { vertexColor: true }
                materials: stageNode.clipped ? cut : original
            }
            Model {
                id: path
                visible: item.active && stageNode.geometryData.kind==="PATH"
                geometry: PathGeometry { assetId: stageNode.geometryData.kind==="PATH" ? item.handle : 0; chunk: item.chunk }
                materials: DefaultMaterial { diffuseColor: item.color; lighting: DefaultMaterial.NoLighting; lineWidth: 3 }
            }
            Model {
                visible: item.active && stageNode.geometryData.kind==="POINT"
                source: "#Sphere"; scale: Qt.vector3d(root.distance*.00012,root.distance*.00012,root.distance*.00012)
                materials: DefaultMaterial { diffuseColor: item.color; lighting: DefaultMaterial.NoLighting }
            }
            ResourceLoader { geometries: [surface.geometry,heat.geometry,path.geometry] }
        }
    }
    Model {
        objectName: "stackingFootprint"
        geometry: ControlGeometry { points: evidence.data.footprint || []; segments: true; stroke: root.distance*.001 }
        materials: DefaultMaterial { diffuseColor: "#76e6cc"; lighting: DefaultMaterial.NoLighting; cullMode: Material.NoCulling }
    }
    Repeater3D {
        model: section.data.contours || []
        delegate: Model {
            required property var modelData
            geometry: ControlGeometry { points: modelData.lines; segments: true; stroke: root.distance*.0015 }
            materials: DefaultMaterial { diffuseColor: modelData.stage===evidence.data.stage ? "#ffbbce" : "#78d9b5"; lighting: DefaultMaterial.NoLighting; cullMode: Material.NoCulling }
        }
    }
    Model {
        objectName: "tissueInspectionWitness"
        geometry: ControlGeometry { objectName: "tissueInspectionLines"; points: evidence.data.lines || []; segments: true; stroke: root.distance*.0015 }
        materials: DefaultMaterial { diffuseColor: "#ffe571"; lighting: DefaultMaterial.NoLighting; cullMode: Material.NoCulling }
    }
}
