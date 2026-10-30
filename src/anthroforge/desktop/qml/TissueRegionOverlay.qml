import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick3D
import AnthroForge.Native 1.0

Model {
    id: overlay
    required property real distance
    visible: App.tissueRegionTools.state.active
    geometry: ControlGeometry { points: App.tissueRegionTools.state.lines || []; segments: true; stroke: overlay.distance*.0014 }
    materials: DefaultMaterial { diffuseColor: "#86e1ad"; lighting: DefaultMaterial.NoLighting; cullMode: Material.NoCulling }
}
