import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiSection {
    id: panel
    objectName: "dependencyInspector"; title: "Relationships & attachments"; expanded: false
    readonly property var detail: workspace.inspectionPanel.detail
    readonly property var attachment: detail.attachment || {}
    readonly property var binding: attachment.binding || {}
    onExpandedChanged: workspace.inspectionPanel.activate(expanded && visible)
    onVisibleChanged: workspace.inspectionPanel.activate(expanded && visible)
    function vector(values) { return values ? values.map(v=>(v/workspace.state.unit_factor).toFixed(3)).join(", ")+" "+workspace.state.display_units : "Unavailable"; }
    Label { text: "Authored generation "+(panel.detail.generation || 0)+" · accepted result "+(panel.detail.result?.revision || 0); wrapMode: Text.Wrap; Layout.fillWidth: true; color: Theme.muted }
    Label { text: "Result: "+(panel.detail.result?.status || "unavailable"); color: Theme.muted }
    Label { text: "Support: "+(panel.attachment.support_name || panel.attachment.follow || "None"); elide: Text.ElideMiddle; Layout.fillWidth: true; color: Theme.muted }
    Label { text: "Parent anchor: "+(panel.attachment.settings?.parent_mode || "—")+"\nChild anchor: "+(panel.attachment.settings?.child_mode || "—"); color: Theme.muted; wrapMode: Text.Wrap; Layout.fillWidth: true }
    Label { text: panel.attachment.captured && panel.attachment.settings?.parent_mode==="SURFACE_NEAREST" ? "Captured surface vertices: "+(panel.binding.surface_vertices || []).join(", ")+"\nBarycentric: "+(panel.binding.barycentric || []).map(v=>v.toFixed(4)).join(", ")+"\nFrame offset: "+panel.vector(panel.binding.frame_offset_metres) : "Origin attachment · offset: "+panel.vector(panel.binding.frame_offset_metres); wrapMode: Text.Wrap; Layout.fillWidth: true; color: Theme.muted }
    Label { visible: !!panel.attachment.anchors?.available; text: "Owner anchor: "+panel.vector(panel.attachment.anchors?.owner_world_metres)+"\nSupport anchor: "+panel.vector(panel.attachment.anchors?.support_world_metres); wrapMode: Text.Wrap; Layout.fillWidth: true; color: Theme.muted }
    Label { visible: !!panel.detail.geometry?.available; text: (panel.detail.geometry?.vertices || 0)+" vertices · "+(panel.detail.geometry?.triangles || 0)+" triangles"; color: Theme.muted }
    Repeater {
        model: panel.detail.relationships || []
        ColumnLayout {
            required property var modelData
            Layout.fillWidth: true
            Label { text: modelData.output+(modelData.participant ? " · in cycle" : modelData.blocked ? " · blocked upstream" : ""); color: modelData.blocked ? Theme.danger : Theme.accent }
            Label { text: "Driven by"; color: Theme.muted; font.pixelSize: 10 }
            Repeater { model: modelData.inputs; RelatedObject { required property var modelData; targetId: modelData.owner; label: modelData.name+" · "+modelData.output } }
            Label { text: "Drives"; color: Theme.muted; font.pixelSize: 10 }
            Repeater { model: modelData.consumers; RelatedObject { required property var modelData; targetId: modelData.owner; label: modelData.name+" · "+modelData.output } }
        }
    }
    Label { text: (panel.detail.topology_locks || []).length ? "Topology locked by" : "Topology is unlocked"; color: Theme.muted }
    Repeater { model: panel.detail.topology_locks || []; RelatedObject { required property var modelData; targetId: modelData.id; label: modelData.name+" · "+modelData.reason } }
}
