import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: row
    required property var measurement
    required property var viewport
    property bool expanded: false
    signal toggleDetails()
    Layout.fillWidth: true; spacing: 4
    function xyz(point) { return point.map(v=>(v/App.runtime.state.unit_factor).toFixed(3)).join(", "); }
    RowLayout {
        Layout.fillWidth: true; spacing: 4
        UiButton { objectName: "measurementDetails"; text: row.expanded ? "−" : "+"; hint: "Show or hide XYZ coordinates"; flatStyle: true; implicitWidth: 24; onClicked: row.toggleDetails() }
        Label { objectName: "measurementDistance"; Layout.fillWidth: true; color: row.measurement.stale ? Theme.accent : Theme.text; text: row.measurement.name+": "+row.viewport.formatLength(row.measurement.distance)+(row.measurement.stale ? " · stale" : ""); elide: Text.ElideRight; ToolTip.visible: hover.hovered; ToolTip.text: text; HoverHandler { id: hover } }
        UiButton { glyph: "delete"; flatStyle: true; hint: "Remove measurement"; onClicked: App.runtime.run("measurement.remove",{measurement:row.measurement.id}) }
    }
    Label { objectName: "measurementCoordinates"; visible: row.expanded; Layout.fillWidth: true; Layout.leftMargin: 28; wrapMode: Text.WrapAnywhere; color: Theme.muted; text: "A: "+row.xyz(row.measurement.start.position)+"\nB: "+row.xyz(row.measurement.end.position)+"\nΔ: "+row.xyz(row.measurement.delta)+" "+App.runtime.state.display_units; lineHeight: 1.4 }
}
