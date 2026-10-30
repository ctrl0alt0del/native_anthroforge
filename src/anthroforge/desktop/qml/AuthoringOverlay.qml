import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick3D
import AnthroForge.Native 1.0

Node {
    id: overlay
    required property real distance
    visible: App.authoring.visible
    Model {
        geometry: ControlGeometry { points: App.authoring.visualLayers.curves || []; segments: true; stroke: overlay.distance*.0016 }
        materials: DefaultMaterial { diffuseColor: Theme.curveColor; lighting: DefaultMaterial.NoLighting; cullMode: Material.NoCulling }
    }
    Model {
        opacity: 0.45
        geometry: ControlGeometry { points: App.authoring.visualLayers.links || []; segments: true }
        materials: DefaultMaterial { diffuseColor: Theme.handleColor; lighting: DefaultMaterial.NoLighting }
    }
    Model {
        geometry: ControlGeometry { points: App.authoring.hoveredLines; segments: true; stroke: overlay.distance*.0018 }
        materials: DefaultMaterial { diffuseColor: Theme.curveHoverColor; lighting: DefaultMaterial.NoLighting; cullMode: Material.NoCulling }
    }
    Repeater3D {
        model: [{kind:"points",color:Theme.curvePointColor}, {kind:"handles",color:Theme.handleColor},
            {kind:"other",color:Theme.controlColor}, {kind:"fieldLow",color:"#418ddd"},
            {kind:"fieldMid",color:"#f0c55c"}, {kind:"fieldHigh",color:"#ee6363"}]
        delegate: Node {
            required property var modelData
            Model {
                objectName: "components_" + modelData.kind
                geometry: ControlGeometry { points: App.authoring.visualLayers[modelData.kind] || []; radius: overlay.distance*.0045 }
                materials: DefaultMaterial { diffuseColor: modelData.color; lighting: DefaultMaterial.NoLighting; cullMode: Material.NoCulling }
            }
            Model {
                geometry: ControlGeometry { points: App.authoring.highlights[modelData.kind] || []; radius: overlay.distance*.0065 }
                materials: DefaultMaterial { diffuseColor: modelData.color; lighting: DefaultMaterial.NoLighting; cullMode: Material.NoCulling }
            }
        }
    }
}
