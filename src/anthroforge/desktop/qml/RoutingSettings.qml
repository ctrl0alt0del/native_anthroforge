import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    required property var curve
    property bool topologyLocked: false
    readonly property var settings: curve.engine_settings || {}
    visible: curve.engine === "ROUTED"
    Layout.fillWidth: true; spacing: Theme.gap
    function updateSetting(key,value) {
        const args={curve:curve.id}; args[key]=value;
        workspace.run("curve.engine_settings",args);
    }
    NumericSetting {
        objectName: "routingClearance"; label: "Surface clearance"; length: true; value: panel.settings.radius || 0
        hint: "Desired centerline distance from obstacles. Bound or touching authored points may contact their surface. This is not curve thickness."
        onEdited: value=>panel.updateSetting("radius",value)
    }
    RoutingObstacles { curve: panel.curve; settings: panel.settings; onEdited: values=>workspace.run("curve.engine_settings",{curve:panel.curve.id,obstacle_mode:values.obstacle_mode,obstacles:values.obstacles || [],excluded_obstacles:values.excluded_obstacles || []}) }
    UiButton { id: advanced; objectName: "routingAdvanced"; text: checked ? "▾  Advanced" : "▸  Advanced"; checkable: true; flatStyle: true }
    ColumnLayout {
        visible: advanced.checked; Layout.fillWidth: true
        NumericSetting { objectName: "routingSamples"; label: "Path resolution"; decimals: 0; value: panel.settings.samples || 64; enabled: !panel.topologyLocked; hint: "Number of evaluated samples, not editable points. More detail costs computation and does not guarantee a valid route."; onEdited: value=>panel.updateSetting("samples",Math.round(value)) }
        NumericSetting { label: "Iteration budget"; decimals: 0; value: panel.settings.accepted_steps || 24; hint: "Maximum accepted optimization updates. Rejected trials may also run; this is not a time limit."; onEdited: value=>panel.updateSetting("accepted_steps",Math.round(value)) }
    }
}
