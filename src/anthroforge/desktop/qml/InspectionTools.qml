import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: tools
    required property var viewport
    readonly property var model: workspace.inspectionTools
    property bool expanded: false
    width: Math.min(320, viewport.width-24)
    height: expanded ? Math.min(content.implicitHeight+header.height+32, viewport.height-100) : header.height+16
    color: Theme.panel; border.color: Theme.border; radius: 4
    function xyz(point) { return point.map(v=>(v/workspace.state.unit_factor).toFixed(3)).join(", "); }
    function saveBookmark() { viewport.storeCamera(); workspace.run("bookmark.add",{name:bookmarkName.text.trim() || "Inspection view"}); }
    ColumnLayout {
        anchors.fill: parent; anchors.margins: Theme.gap; spacing: Theme.gap
        RowLayout {
            id: header
            UiButton { objectName: "inspectionToolsToggle"; text: "Measurements & views"; flatStyle: true; alignLeft: true; Layout.fillWidth: true; onClicked: tools.expanded=!tools.expanded }
            UiButton { objectName: "measureSurface"; text: "Ruler"; checked: tools.model.state.active; enabled: !viewport.transforming && !workspace.state.waiting; hint: "Pick two surface points · Esc to finish"; onClicked: { tools.expanded=true; tools.model.toggle(); viewport.forceActiveFocus(); } }
        }
        ScrollView {
            id: scroll; rightPadding: effectiveScrollBarWidth; visible: tools.expanded; Layout.fillWidth: true; Layout.fillHeight: true; clip: true; contentWidth: availableWidth
            ColumnLayout {
                id: content; width: scroll.availableWidth; spacing: Theme.gap
                Label { visible: tools.model.state.active; Layout.fillWidth: true; wrapMode: Text.WordWrap; color: Theme.accent; text: "Pick "+(tools.model.state.start.entity ? "second" : "first")+" surface point · Esc to finish" }
                Label { Layout.fillWidth: true; wrapMode: Text.WrapAnywhere; color: Theme.muted; visible: !!tools.model.state.hover.entity; text: tools.model.state.hover.position ? "XYZ: "+tools.xyz(tools.model.state.hover.position)+" "+workspace.state.display_units : "" }
                UiSection {
                    title: "Measurements"; hint: "Pick two surface points with Ruler. Alt-click reaches deeper surfaces. Expand a measurement for XYZ coordinates. Rulers keep fixed coordinates; changed surfaces are marked stale."
                    Label { visible: !tools.model.state.measurements.length; text: "No measurements yet"; color: Theme.muted }
                    Repeater { model: tools.model.state.measurements; MeasurementRow { required property var modelData; measurement: modelData; viewport: tools.viewport } }
                }
                UiSection {
                    title: "Named cameras"; hint: "Save the current camera, then use Go to restore it. Restoring a view preserves an active edit."
                RowLayout {
                    UiField { id: bookmarkName; objectName: "bookmarkName"; Layout.fillWidth: true; placeholderText: "View name" }
                    UiButton { objectName: "saveBookmark"; text: "Save"; enabled: !workspace.state.waiting; onClicked: tools.saveBookmark() }
                }
                Repeater {
                    model: tools.model.state.bookmarks
                    RowLayout {
                        required property var modelData
                        UiField { id: nameField; Layout.fillWidth: true; text: modelData.name; onEditingFinished: { if(text.trim() && text!==modelData.name) workspace.run("bookmark.rename",{bookmark:modelData.id,name:text}); } }
                        UiButton { objectName: "restoreBookmark"; text: "Go"; enabled: !workspace.state.waiting; onClicked: { tools.model.restoreBookmark(modelData.id); viewport.forceActiveFocus(); } }
                        UiButton { glyph: "delete"; flatStyle: true; hint: "Remove bookmark"; onClicked: workspace.run("bookmark.remove",{bookmark:modelData.id}) }
                    }
                }
                }
            }
        }
    }
}
