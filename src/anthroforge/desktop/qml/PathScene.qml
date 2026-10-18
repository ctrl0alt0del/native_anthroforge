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
            // Instances own the complete application-Z-up to Qt-Y-up frame.
            // Keeping this outside the rotated anatomy node avoids an ambiguous instance root.
            instancing: AffineInstance {
                frame: { const m=item.matrix; return [m[0],m[1],m[2],m[3],m[8],m[9],m[10],m[11],-m[4],-m[5],-m[6],-m[7],0,0,0,1]; }
            }
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
