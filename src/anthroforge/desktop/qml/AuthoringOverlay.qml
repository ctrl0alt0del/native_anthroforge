import QtQuick
import QtQuick3D
import AnthroForge.Native 1.0

Node {
    id: overlay
    required property real distance
    visible: authoring.visible
    Model {
        geometry: ControlGeometry { points: authoring.visualLayers.curves || []; segments: true; stroke: overlay.distance*.0016 }
        materials: DefaultMaterial { diffuseColor: Theme.curveColor; lighting: DefaultMaterial.NoLighting; cullMode: Material.NoCulling }
    }
    Model {
        opacity: 0.45
        geometry: ControlGeometry { points: authoring.visualLayers.links || []; segments: true }
        materials: DefaultMaterial { diffuseColor: Theme.handleColor; lighting: DefaultMaterial.NoLighting }
    }
    Model {
        geometry: ControlGeometry { points: authoring.hoveredLines; segments: true; stroke: overlay.distance*.0018 }
        materials: DefaultMaterial { diffuseColor: Theme.curveHoverColor; lighting: DefaultMaterial.NoLighting; cullMode: Material.NoCulling }
    }
    Repeater3D {
        model: [{kind:"points",color:Theme.curvePointColor}, {kind:"handles",color:Theme.handleColor},
            {kind:"other",color:Theme.controlColor}]
        delegate: Node {
            required property var modelData
            Model {
                objectName: "components_" + modelData.kind
                geometry: ControlGeometry { points: authoring.visualLayers[modelData.kind] || []; radius: overlay.distance*.0045 }
                materials: DefaultMaterial { diffuseColor: modelData.color; lighting: DefaultMaterial.NoLighting; cullMode: Material.NoCulling }
            }
            Model {
                geometry: ControlGeometry { points: authoring.highlights[modelData.kind] || []; radius: overlay.distance*.0065 }
                materials: DefaultMaterial { diffuseColor: modelData.color; lighting: DefaultMaterial.NoLighting; cullMode: Material.NoCulling }
            }
        }
    }
}
