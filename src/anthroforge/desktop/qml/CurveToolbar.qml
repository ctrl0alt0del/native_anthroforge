import QtQuick
import QtQuick.Controls

Column {
    id: toolbar
    required property var keyboard
    readonly property var tool: workspace.drawingTools
    spacing: 5
    UiButton { objectName: "addConstructionPoint"; width: 34; height: 34; glyph: "point-add"; hint: "Add Point at 3D cursor"; onClicked: workspace.createPoint() }
    UiButton { objectName: "addCurveAtCursor"; width: 34; height: 34; glyph: "curve-add"; hint: "Add Curve at 3D cursor"; onClicked: toolbar.tool.addCurve() }
    UiButton {
        id: placeButton
        objectName: "placeCurvePoints"; width: 34; height: 34
        glyph: toolbar.tool.state.placement_mode==="BRANCH" ? "curve-branch" : "curve-points"
        checked: ["POINTS","BRANCH"].includes(toolbar.tool.state.mode)
        hint: (toolbar.tool.state.placement_mode==="BRANCH" ? "Place Branched Points" : "Place Points")+" · Right-click for tools · "+toolbar.keyboard.modifierName("continuePlacement")+" + click to continue; plain click finishes from point 2"
        onClicked: checked ? toolbar.tool.cancel() : toolbar.tool.begin(toolbar.tool.state.placement_mode)
        ContextMenu.onRequested: position => pointTools.popup(placeButton.width+6,0)
        TapHandler { acceptedButtons: Qt.RightButton; onTapped: pointTools.popup(placeButton.width+6,0) }
        UiMenu {
            id: pointTools
            UiMenuItem { objectName: "regularPointPlacement"; text: "Place Points"; checked: toolbar.tool.state.placement_mode==="POINTS"; onTriggered: toolbar.tool.begin("POINTS") }
            UiMenuItem { objectName: "branchedPointPlacement"; text: "Place Branched Points"; checked: toolbar.tool.state.placement_mode==="BRANCH"; onTriggered: toolbar.tool.begin("BRANCH") }
        }
        Text { anchors.right: parent.right; anchors.bottom: parent.bottom; anchors.margins: 2; text: "▾"; color: Theme.muted; font.pixelSize: 8 }
    }
    UiButton { objectName: "drawCurve"; width: 34; height: 34; glyph: "curve-draw"; checked: toolbar.tool.state.mode==="DRAW"; hint: "Draw Curve · Release to finish a stroke"; onClicked: checked ? toolbar.tool.cancel() : toolbar.tool.begin("DRAW") }
    UiButton { objectName: "placeCursor"; width: 34; height: 34; glyph: "cursor"; checked: toolbar.tool.state.mode==="CURSOR"; hint: "3D cursor · Surface placement and numeric settings"; onClicked: checked ? toolbar.tool.cancel() : toolbar.tool.begin("CURSOR") }
    UiButton { objectName: "createPatchSurface"; width: 34; height: 34; glyph: "patch"; hint: workspace.surfaceAction.hint; enabled: workspace.surfaceAction.enabled; onClicked: workspace.createSurface("AUTO") }
}
