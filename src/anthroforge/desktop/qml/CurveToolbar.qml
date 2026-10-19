import QtQuick

Column {
    id: toolbar
    required property var keyboard
    readonly property var tool: workspace.drawingTools
    spacing: 5
    UiButton { objectName: "addCurveAtCursor"; width: 34; height: 34; glyph: "curve-add"; hint: "Add Curve at 3D cursor"; onClicked: toolbar.tool.addCurve() }
    UiButton { objectName: "placeCurvePoints"; width: 34; height: 34; glyph: "curve-points"; checked: toolbar.tool.state.mode==="POINTS"; hint: "Place Points · "+toolbar.keyboard.modifierName("continuePlacement")+" + click to continue; plain click finishes from point 2"; onClicked: checked ? toolbar.tool.cancel() : toolbar.tool.begin("POINTS") }
    UiButton { objectName: "drawCurve"; width: 34; height: 34; glyph: "curve-draw"; checked: toolbar.tool.state.mode==="DRAW"; hint: "Draw Curve · Release to finish a stroke"; onClicked: checked ? toolbar.tool.cancel() : toolbar.tool.begin("DRAW") }
    UiButton { objectName: "placeCursor"; width: 34; height: 34; glyph: "cursor"; checked: toolbar.tool.state.mode==="CURSOR"; hint: "3D cursor · Surface placement and numeric settings"; onClicked: checked ? toolbar.tool.cancel() : toolbar.tool.begin("CURSOR") }
    UiButton { objectName: "createPatchSurface"; width: 34; height: 34; glyph: "patch"; hint: "Patch selected closed curve"; enabled: workspace.selectedObjects.length>0; onClicked: workspace.createSurface("PATCH") }
}
