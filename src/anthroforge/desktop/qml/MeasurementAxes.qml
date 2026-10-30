import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick3D
import AnthroForge.Native 1.0

Node {
    id: root
    required property real distance
    ViewSnapshot { id: evidence; source: App.surfaceMeasurements }
    Model {
        geometry: ControlGeometry { points:evidence.data.volume || []; segments:true; stroke:root.distance*.0015 }
        materials: DefaultMaterial { diffuseColor:"#f2ba62"; lighting:DefaultMaterial.NoLighting; cullMode:Material.NoCulling }
    }
    Repeater3D {
        model: evidence.data.lines?.length ? 5 : 0
        delegate: Model {
            required property int index
            readonly property var values: index<3 ? evidence.data.lines : evidence.data.section?.lines || []
            readonly property int offset: 2*(index<3 ? index : index-3)
            geometry: ControlGeometry { points:values.slice(offset,offset+2); segments:true; stroke:root.distance*.001 }
            materials: DefaultMaterial { diffuseColor:["#ed7474","#79d08c","#75a7ef","#f5ca70","#77dfd6"][index]; lighting:DefaultMaterial.NoLighting; cullMode:Material.NoCulling }
        }
    }
}
