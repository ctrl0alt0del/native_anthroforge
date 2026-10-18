import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    readonly property var tool: workspace.drawingTools
    readonly property var options: tool.state.options
    readonly property bool capturing: tool.state.count>0
    spacing: Theme.gap
    UiSection {
        title: "Create curve"
        UiButton { text: "Add Curve at cursor"; Layout.fillWidth: true; onClicked: workspace.drawingTools.addCurve() }
        RowLayout {
            UiButton { text: "Place Points"; Layout.fillWidth: true; checked: panel.tool.state.mode==="POINTS"; onClicked: panel.tool.begin("POINTS") }
            UiButton { text: "Draw"; Layout.fillWidth: true; checked: panel.tool.state.mode==="DRAW"; onClicked: panel.tool.begin("DRAW") }
        }
        ColumnLayout {
            visible: panel.tool.state.mode==="DRAW" || panel.tool.state.mode==="POINTS"; Layout.fillWidth: true
            UiCombo { Layout.fillWidth: true; enabled: !panel.capturing; model: ["VIEW","SURFACE","IMAGE"]; currentIndex: model.indexOf(panel.options.depth); onActivated: panel.tool.setting("depth",currentText) }
            Label { text: panel.options.depth==="VIEW" ? "View plane through the 3D cursor" : panel.options.depth==="SURFACE" ? "Project onto visible geometry" : "Trace in the selected image's plane"; color: Theme.muted; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            UiCheck { visible: panel.options.depth==="SURFACE"; enabled: !panel.capturing; text: "Selected geometry only"; checked: panel.options.selected_only; onClicked: panel.tool.setting("selected_only",checked) }
            UiCombo { visible: panel.options.depth==="SURFACE"; enabled: !panel.capturing; Layout.fillWidth: true; model: ["Follow surfaces","First hit · view plane","First hit · surface plane"]; currentIndex: panel.options.first_plane; onActivated: panel.tool.setting("first_plane",currentIndex) }
            NumericSetting { visible: panel.options.depth==="SURFACE"; enabled: !panel.capturing; label: "Surface offset"; value: panel.options.offset; length: !panel.options.relative; onEdited: value=>panel.tool.setting("offset",value) }
            UiCheck { visible: panel.options.depth==="SURFACE"; enabled: !panel.capturing; text: "Offset relative to radius"; checked: panel.options.relative; onClicked: panel.tool.setting("relative",checked) }
            UiCombo { enabled: !panel.capturing; Layout.fillWidth: true; model: ["REFIT","SPLIT","POLYLINE"]; currentIndex: model.indexOf(panel.options.method); onActivated: panel.tool.setting("method",currentText) }
            NumericSetting { enabled: !panel.capturing; visible: panel.tool.state.mode==="DRAW" && panel.options.method!=="POLYLINE"; label: "Fit error"; length: true; value: panel.options.error; onEdited: value=>panel.tool.setting("error",value) }
            NumericSetting { enabled: !panel.capturing; visible: panel.tool.state.mode==="DRAW" && panel.options.method!=="POLYLINE"; label: "Corner angle · degrees"; value: panel.options.corner_angle; onEdited: value=>panel.tool.setting("corner_angle",value) }
            NumericSetting { enabled: !panel.capturing; label: "Radius"; value: panel.options.radius; onEdited: value=>panel.tool.setting("radius",value) }
            UiCheck { enabled: !panel.capturing; text: "Closed curve"; checked: panel.options.closed; onClicked: panel.tool.setting("closed",checked) }
            Label { text: panel.tool.state.mode==="DRAW" ? "Release to finish · Draw again to create another" : "Click to place · Enter to finish · Backspace to remove"; color: Theme.muted; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            RowLayout {
                UiButton { visible: panel.tool.state.mode==="POINTS"; text: "Finish curve"; enabled: panel.tool.state.count>=2; onClicked: panel.tool.finish() }
                UiButton { text: "Exit tool"; onClicked: panel.tool.cancel() }
            }
        }
    }
    UiSection {
        title: "3D cursor"
        VectorSetting { label: "World position"; length: true; values: workspace.state.cursor || [0,0,0]; onEdited: values=>workspace.run("workspace.update",{cursor:values}) }
        UiButton { text: "Place on surface"; checked: panel.tool.state.mode==="CURSOR"; Layout.fillWidth: true; onClicked: panel.tool.begin("CURSOR") }
    }
}
