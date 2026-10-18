import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    required property var curve
    required property var point
    readonly property var binding: (curve.bindings || []).find(b=>b.point===point.id) || null
    readonly property var surfaces: { const revision=workspace.state.revision; return workspace.anatomicalSurfaces(); }
    readonly property string targetName: binding ? (surfaces.find(s=>s.id===binding.target)?.name || "Missing surface") : ""
    visible: !!binding; Layout.fillWidth: true; spacing: Theme.gap
    Label { text: "Attachment: "+panel.targetName; color: Theme.muted; Layout.fillWidth: true; elide: Text.ElideRight }
    UiCombo {
        objectName: "fiberBindingScope"; Layout.fillWidth: true
        model: ["Current parent", "Any eligible parent"]
        currentIndex: panel.binding?.capture_scope === "ANY_PARENT" ? 1 : 0
        hint: "Choose eligible surfaces when this bound point is edited"
        onActivated: workspace.run("fiber.binding.scope",{curve:panel.curve.id,point:panel.point.id,scope:currentIndex===1?"ANY_PARENT":"CURRENT_PARENT"})
    }
}
