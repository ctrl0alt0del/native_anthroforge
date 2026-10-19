import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    required property var item
    readonly property bool anchor: item.kind === "ANCHOR"
    Layout.fillWidth: true; spacing: Theme.gap
    UiSection {
        title: panel.anchor ? "Anchor" : "Point"
        VectorSetting { visible: !panel.anchor; label: "Local position"; length: true; values: panel.item.point_position || [0,0,0]; onEdited: values=>workspace.run("construction.point.update",{target:panel.item.id,position:values}) }
        UiDetail { label: "World position"; value: (panel.item.world_position || []).map(v=>v.toFixed(4)).join(", ")+" m" }
        UiDetail { visible: panel.anchor; label: "Binding"; value: "Retained surface location" }
    }
    UiSection {
        title: panel.anchor ? "Explicit rebind" : "Create attached copy"
        SurfaceSelector { id: surface; objectName: "pointAttachmentSurface"; target: panel.item.binding?.reference?.target || ""; role: panel.item.binding?.reference?.role || "" }
        UiButton {
            objectName: "createOrRebindAnchor"; Layout.fillWidth: true
            text: panel.anchor ? "Rebind at 3D cursor" : "Create independent Anchor"
            enabled: !!surface.current.ready
            onClicked: {
                const args={parent:surface.current.id,role:surface.current.role};
                if(panel.anchor) { args.target=panel.item.id; args.position=workspace.state.cursor; workspace.run("anchor.rebind",args); }
                else { args.source=panel.item.id; workspace.createConstruction("anchor.create",args); }
            }
        }
    }
}
