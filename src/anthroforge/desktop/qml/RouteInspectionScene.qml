import QtQuick
import QtQuick3D
import AnthroForge.Native 1.0

Node {
    required property real distance
    Repeater3D {
        model: workspace.routeInspection.state.paths
        delegate: Model {
            required property var modelData
            geometry: ControlGeometry { points: modelData.points; stroke: distance*.0018 }
            materials: DefaultMaterial { diffuseColor: modelData.color; lighting: DefaultMaterial.NoLighting; cullMode: Material.NoCulling }
        }
    }
    Model {
        objectName: "routeContactWitnesses"
        geometry: ControlGeometry { points: workspace.routeInspection.state.contacts; segments: true; stroke: distance*.002 }
        materials: DefaultMaterial { diffuseColor: "#ff7969"; lighting: DefaultMaterial.NoLighting; cullMode: Material.NoCulling }
    }
}
