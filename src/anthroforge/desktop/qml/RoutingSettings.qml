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
    NumericSetting { objectName: "routingSamples"; label: "Path samples"; decimals: 0; value: panel.settings.samples || 64; enabled: !panel.topologyLocked; onEdited: value=>panel.updateSetting("samples",Math.round(value)) }
    NumericSetting { objectName: "routingClearance"; label: "Surface clearance"; length: true; value: panel.settings.radius || 0; onEdited: value=>panel.updateSetting("radius",value) }
    NumericSetting { label: "Accepted solve steps"; decimals: 0; value: panel.settings.accepted_steps || 24; onEdited: value=>panel.updateSetting("accepted_steps",Math.round(value)) }
    RoutingObstacles {
        curve: panel.curve; selected: panel.settings.obstacles || []
        onEdited: values=>panel.updateSetting("obstacles",values)
    }
}
