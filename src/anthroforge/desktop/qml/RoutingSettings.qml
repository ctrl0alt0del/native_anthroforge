import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    required property var curve
    property bool topologyLocked: false
    readonly property var settings: curve.engine_settings || {}
    readonly property var surfaces: { const revision=workspace.state.revision; return workspace.anatomicalSurfaces(); }
    visible: curve.engine === "ROUTED"
    Layout.fillWidth: true; spacing: Theme.gap
    function updateSetting(key,value) {
        const args={curve:curve.id}; args[key]=value;
        workspace.run("curve.engine_settings",args);
    }
    function toggleObstacle(id,enabled) {
        const ids=settings.obstacles || [];
        updateSetting("obstacles",enabled ? ids.concat([id]) : ids.filter(key=>key!==id));
    }
    NumericSetting { objectName: "routingSamples"; label: "Path samples"; decimals: 0; value: panel.settings.samples || 64; enabled: !panel.topologyLocked; onEdited: value=>panel.updateSetting("samples",Math.round(value)) }
    NumericSetting { objectName: "routingClearance"; label: "Surface clearance"; length: true; value: panel.settings.radius || 0; onEdited: value=>panel.updateSetting("radius",value) }
    NumericSetting { label: "Accepted solve steps"; decimals: 0; value: panel.settings.accepted_steps || 24; onEdited: value=>panel.updateSetting("accepted_steps",Math.round(value)) }
    UiButton { id: expand; text: "Routing obstacles"; checkable: true; Layout.fillWidth: true }
    ColumnLayout {
        visible: expand.checked; Layout.fillWidth: true
        Label { text: "Attachment surfaces are included automatically."; color: Theme.muted; wrapMode: Text.WordWrap; Layout.fillWidth: true }
        Repeater {
            model: panel.surfaces
            UiCheck {
                required property var modelData
                objectName: "routingObstacle"
                property string targetId: modelData.id
                text: modelData.name; checked: (panel.settings.obstacles || []).includes(targetId)
                onClicked: panel.toggleObstacle(targetId,checked)
            }
        }
    }
}
