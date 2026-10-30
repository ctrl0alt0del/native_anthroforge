import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick3D
import AnthroForge.Native 1.0

Node {
    id: root
    required property real distance
    ViewSnapshot { id:evidence; source:App.placementInspection }
    Model {
        geometry:ControlGeometry { points:evidence.data.lines || []; segments:true; stroke:root.distance*.0015 }
        materials:DefaultMaterial { diffuseColor:"#ffe571"; lighting:DefaultMaterial.NoLighting; cullMode:Material.NoCulling }
    }
}
