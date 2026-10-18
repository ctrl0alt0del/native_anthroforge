import QtQuick
import QtQuick3D
import AnthroForge.Native 1.0

Repeater3D {
    model: workspace.pathModel
    delegate: Node {
        required property var item
        Model {
            id: path
            objectName: "path_" + item.id + "_" + item.chunk
            visible: item.active && item.visible && !(authoring.state.editing && workspace.selectedId === item.id)
            geometry: PathGeometry { assetId: item.handle; chunk: item.chunk }
            instancing: AffineInstance { frame: item.matrix }
            opacity: item.readonly ? .12 : 1
            materials: DefaultMaterial {
                lighting: DefaultMaterial.NoLighting
                diffuseColor: workspace.selectedObjects.includes(item.id) ? Theme.accent : workspace.hoveredId === item.id ? Theme.curveHoverColor : Theme.curveColor
                lineWidth: 2
            }
        }
        ResourceLoader { geometries: [path.geometry] }
    }
}
