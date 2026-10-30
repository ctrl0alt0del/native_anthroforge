import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    property string fieldName: "collagen"
    property bool collagen: false
    readonly property var tool: App.tissuePainting
    readonly property bool painting: tool.state.active && tool.state.name===fieldName && tool.state.domain===(collagen ? "collagen" : "paint")
    Layout.fillWidth: true
    UiButton {
        objectName: "tissueFieldPaint"; text: panel.painting ? "Finish painting" : panel.collagen ? "Paint collagen" : "Paint field"
        Layout.fillWidth: true; checkable: true; checked: panel.painting
        onClicked: { if(panel.painting) panel.tool.cancel(); else if(panel.collagen) panel.tool.beginCollagen(); else panel.tool.begin(panel.fieldName); }
    }
    ColumnLayout {
        visible: panel.painting; Layout.fillWidth: true
        NumericSetting { label: "Brush radius · px"; value: panel.tool.state.radius; onEdited: value=>panel.tool.setting("radius",value) }
        NumericSetting { label: "Weight · 0–1"; value: panel.tool.state.weight; onEdited: value=>panel.tool.setting("weight",value) }
        NumericSetting { label: "Strength · 0–1"; value: panel.tool.state.strength; onEdited: value=>panel.tool.setting("strength",value) }
        NumericSetting { label: "Falloff power"; value: panel.tool.state.falloff; onEdited: value=>panel.tool.setting("falloff",value) }
        UiCheck { text: "Paint Through"; checked: panel.tool.state.through; onToggled: panel.tool.setting("through",checked) }
        UiNotice { text: panel.tool.state.pending ? "Finishing weight stroke…" : "" }
        Label { text: panel.collagen ? "Blue 0, gold 0.5, red 1. Drag to paint; release commits one stroke." : "Blue 0 · Gold 0.5 · Red 1. Drag to paint; release commits one stroke. Base weights are shared through tissue thickness."; color: Theme.muted; wrapMode: Text.WordWrap; Layout.fillWidth: true }
        UiButton { visible: !panel.collagen; text: "Explain constraints at a point"; Layout.fillWidth: true; onClicked: App.tissueInspection.explain() }
        UiButton { visible: !panel.collagen; text: "Show relaxation displacement"; Layout.fillWidth: true; onClicked: { panel.tool.cancel(); App.tissueInspection.configure("intrinsic","rest","Displacement"); } }
    }
}
