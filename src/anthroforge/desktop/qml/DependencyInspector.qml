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
    UiDetail { label: "Result"; value: panel.detail.result?.status || "Unavailable" }
    UiDetail { label: "Support"; value: panel.attachment.support_name || panel.attachment.follow || "None" }
    UiDetail { label: "Transform parent"; visible: !!panel.attachment.transform_parent; value: panel.attachment.transform_parent_name || "None" }
    UiDetail { label: "Path"; visible: panel.detail.geometry?.kind === "PATH"; value: (panel.detail.geometry?.samples || 0)+" evaluated samples" }
    UiDetail { label: "Surface"; visible: !!panel.detail.geometry?.available && panel.detail.geometry?.kind === "MESH"; value: (panel.detail.geometry?.vertices || 0)+" vertices · "+(panel.detail.geometry?.triangles || 0)+" triangles" }
    Repeater {
        model: panel.detail.relationships || []
        ColumnLayout {
            required property var modelData
            Layout.fillWidth: true
            Label { text: modelData.output+(modelData.participant ? " · in cycle" : modelData.blocked ? " · blocked upstream" : ""); color: modelData.blocked ? Theme.danger : Theme.accent }
            Label { text: "Driven by"; color: Theme.muted; font.pixelSize: 10 }
            RelatedObjects { objectName:"dependencyInputs_"+modelData.output; rows:modelData.inputs }
            Label { text: "Drives"; color: Theme.muted; font.pixelSize: 10 }
            RelatedObjects { objectName:"dependencyConsumers_"+modelData.output; rows:modelData.consumers }
        }
    }
    Label { text: (panel.detail.topology_locks || []).length ? "Topology locked by" : "Topology is unlocked"; color: Theme.muted }
    RelatedObjects { objectName:"topologyConsumers"; rows:panel.detail.topology_locks || [] }
    UiSection {
        title: "Attachment details"; expanded: false
        UiDetail { label: "Authored"; value: String(panel.detail.generation || 0) }
        UiDetail { label: "Accepted"; value: String(panel.detail.result?.revision || 0) }
        UiDetail { label: "Parent anchor"; value: panel.attachment.settings?.parent_mode || "—" }
        UiDetail { label: "Child anchor"; value: panel.attachment.settings?.child_mode || "—" }
        UiDetail { label: "Vertices"; visible: !!panel.attachment.captured && panel.attachment.settings?.parent_mode==="SURFACE_NEAREST"; value: (panel.binding.surface_vertices || []).join(", ") }
        UiDetail { label: "Barycentric"; visible: !!panel.attachment.captured && panel.attachment.settings?.parent_mode==="SURFACE_NEAREST"; value: (panel.binding.barycentric || []).map(v=>v.toFixed(4)).join(", ") }
        UiDetail { label: "Frame offset"; value: panel.attachment.captured ? panel.vector(panel.binding.frame_offset_metres) : "No captured attachment" }
        UiDetail { label: "Owner anchor"; visible: !!panel.attachment.anchors?.available; value: panel.vector(panel.attachment.anchors?.owner_world_metres) }
        UiDetail { label: "Support anchor"; visible: !!panel.attachment.anchors?.available; value: panel.vector(panel.attachment.anchors?.support_world_metres) }
    }
}
