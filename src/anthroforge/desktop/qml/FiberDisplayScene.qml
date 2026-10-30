import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick3D
import AnthroForge.Native 1.0

Repeater3D {
    id: fibers
    property var effects: ({})
    model: App.viewport.fiberDisplayModel
    delegate: Node {
        required property var item
        Model {
            id: surface
            objectName: "fiberDisplay_" + item.id + "_" + item.chunk
            visible: !App.shortcutComparison.before && item.active && item.visible && !(App.authoring.state.editing && App.selection.selectedId===item.id)
            geometry: MeshGeometry { assetId: item.handle; chunk: item.chunk }
            instancing: AffineInstance {
                frame: { const m=item.matrix; return [m[0],m[1],m[2],m[3],m[8],m[9],m[10],m[11],-m[4],-m[5],-m[6],-m[7],0,0,0,1]; }
            }
            opacity: (item.context_dimmed ?? item.readonly) ? .12 : 1
            materials: DefaultMaterial {
                lighting: DefaultMaterial.NoLighting
                cullMode: Material.NoCulling
                diffuseColor: fibers.effects.shown && fibers.effects.colors?.[item.id] ? fibers.effects.colors[item.id] : App.selection.selectedObjects.includes(item.id) ? Theme.accent : App.selection.hoveredId===item.id ? Theme.curveHoverColor : Theme.curveColor
            }
        }
        ResourceLoader { geometries: [surface.geometry] }
    }
}
