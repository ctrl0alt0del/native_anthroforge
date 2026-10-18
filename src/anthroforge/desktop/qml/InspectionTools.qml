import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: tools
    required property var viewport
    readonly property var model: workspace.inspectionTools
    property bool expanded: false
    width: 310; height: expanded ? Math.min(430, viewport.height-100) : 34
    color: Theme.panel; border.color: Theme.border; radius: 4
    function xyz(point) { return point.map(v=>(v*workspace.state.unit_factor).toFixed(3)).join(", "); }
    function saveBookmark() { viewport.storeCamera(); workspace.run("bookmark.add",{name:bookmarkName.text.trim() || "Inspection view"}); }
    ColumnLayout {
        anchors.fill: parent; anchors.margins: 6; spacing: 6
        RowLayout {
            UiButton { objectName: "inspectionToolsToggle"; text: "Measurements & views"; flatStyle: true; Layout.fillWidth: true; onClicked: tools.expanded=!tools.expanded }
            UiButton { objectName: "measureSurface"; text: "Ruler"; checked: tools.model.state.active; enabled: !viewport.transforming && !workspace.state.waiting; hint: "Pick two surface points · Esc to finish"; onClicked: { tools.expanded=true; tools.model.toggle(); viewport.forceActiveFocus(); } }
        }
        ScrollView {
            visible: tools.expanded; Layout.fillWidth: true; Layout.fillHeight: true; clip: true; contentWidth: availableWidth
            ColumnLayout {
                width: parent.width; spacing: 8
                Label { Layout.fillWidth: true; wrapMode: Text.WordWrap; color: Theme.muted; text: tools.model.state.active ? "Pick "+(tools.model.state.start.entity ? "second" : "first")+" surface point. Esc finishes. Alt-click selects deeper surfaces." : "Rulers capture fixed coordinates; changed surfaces are marked stale." }
                Label { Layout.fillWidth: true; wrapMode: Text.WrapAnywhere; color: Theme.accent; visible: !!tools.model.state.hover.entity; text: tools.model.state.hover.position ? "XYZ: "+tools.xyz(tools.model.state.hover.position)+" "+workspace.state.display_units : "" }
                Repeater {
                    model: tools.model.state.measurements
                    ColumnLayout {
                        required property var modelData
                        Layout.fillWidth: true
                        RowLayout {
                            Label { Layout.fillWidth: true; color: modelData.stale ? "#ffcc64" : Theme.text; text: modelData.name+": "+(modelData.distance*workspace.state.unit_factor).toFixed(3)+" "+workspace.state.display_units+(modelData.stale ? " · stale" : "") }
                            UiButton { glyph: "delete"; flatStyle: true; hint: "Remove measurement"; onClicked: workspace.run("measurement.remove",{measurement:modelData.id}) }
                        }
                        Label { Layout.fillWidth: true; wrapMode: Text.WrapAnywhere; color: Theme.muted; text: "A: "+tools.xyz(modelData.start.position)+"\nB: "+tools.xyz(modelData.end.position)+"\nΔ: "+tools.xyz(modelData.delta)+" "+workspace.state.display_units }
                    }
                }
                Label { text: "Named cameras"; color: Theme.text; font.bold: true }
                RowLayout {
                    UiField { id: bookmarkName; objectName: "bookmarkName"; Layout.fillWidth: true; placeholderText: "View name" }
                    UiButton { objectName: "saveBookmark"; text: "Save"; enabled: !workspace.state.waiting; onClicked: tools.saveBookmark() }
                }
                Repeater {
                    model: tools.model.state.bookmarks
                    RowLayout {
                        required property var modelData
                        UiField { id: nameField; Layout.fillWidth: true; text: modelData.name; onEditingFinished: { if(text.trim() && text!==modelData.name) workspace.run("bookmark.rename",{bookmark:modelData.id,name:text}); } }
                        UiButton { text: "Go"; enabled: !workspace.state.waiting; onClicked: { tools.model.restoreBookmark(modelData.id); viewport.forceActiveFocus(); } }
                        UiButton { glyph: "delete"; flatStyle: true; hint: "Remove bookmark"; onClicked: workspace.run("bookmark.remove",{bookmark:modelData.id}) }
                    }
                }
            }
        }
    }
}
