import QtQuick
import QtQuick3D
import AnthroForge.Native 1.0

Repeater3D {
    id: images
    required property string layer
    required property bool orthographic
    required property vector3d viewAxis
    property bool historical: false
    model: historical ? workspace.shortcutComparison.imageLayer(layer) : workspace.imageLayer(layer)
    delegate: Node {
        required property var item
        readonly property var style: item.image_style
        Model {
            id: tile
            objectName: "image_" + item.id + "_" + item.chunk
            visible: (images.historical || !workspace.shortcutComparison.before) && item.active && item.visible && (images.orthographic ? style.orthographic : style.perspective) && (!style.only_axis_aligned || imageGeometry.axisAligned(images.viewAxis, item.matrix))
            opacity: style.opacity * (item.readonly ? .12 : 1) * (images.historical && workspace.shortcutComparison.state.mode === "Overlay" ? .3 : 1)
            geometry: ImageGeometry { id: imageGeometry; assetId: item.handle; tile: item.chunk; dimensions: Qt.size(item.content.dimensions[0],item.content.dimensions[1]); frame: item.matrix }
            materials: DefaultMaterial {
                lighting: DefaultMaterial.NoLighting
                cullMode: style.side === "FRONT" ? Material.BackFaceCulling : style.side === "BACK" ? Material.FrontFaceCulling : Material.NoCulling
                diffuseColor: "white"
                diffuseMap: Texture {
                    id: imageMap
                    textureData: ImageTexture { assetId: item.handle; tile: item.chunk }
                    autoOrientation: false
                    tilingModeHorizontal: Texture.ClampToEdge
                    tilingModeVertical: Texture.ClampToEdge
                    minFilter: Texture.Linear
                    magFilter: Texture.Linear
                }
            }
        }
        ResourceLoader { geometries: [tile.geometry]; textures: [imageMap] }
    }
}
