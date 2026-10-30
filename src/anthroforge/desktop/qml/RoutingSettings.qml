import AnthroForge.Desktop 1.0
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
        App.runtime.run("curve.engine_settings",args);
    }
    NumericSetting {
        propertyReference: ({target:panel.curve.id,path:["engine_settings","radius"]}); objectName: "routingClearance"; label: "Surface clearance"; length: true; value: panel.settings.radius || 0
        hint: "Desired centerline distance from obstacles. Bound or touching authored points may contact their surface. This is not curve thickness."
        onEdited: value=>panel.updateSetting("radius",value)
    }
    RoutingObstacles { curve: panel.curve; settings: panel.settings; onEdited: values=>App.runtime.run("curve.engine_settings",{curve:panel.curve.id,obstacle_mode:values.obstacle_mode,obstacles:values.obstacles || [],excluded_obstacles:values.excluded_obstacles || []}) }
    RouteInspection { }
    UiButton { objectName:"routingColdRecalculate"; text:"Recalculate from planner"; Layout.fillWidth:true; hint:"Run an authoritative cold calculation; keep the accepted path until success"; onClicked:App.runtime.run("curve.reroute",{curve:panel.curve.id}) }
    UiButton { id: advanced; objectName: "routingAdvanced"; text: checked ? "▾  Advanced" : "▸  Advanced"; checkable: true; flatStyle: true }
    ColumnLayout {
        visible: advanced.checked; Layout.fillWidth: true
        UiCheck { objectName:"routingWarmStart"; text:"Use warm start"; checked:panel.settings.use_warm_start !== false; hint:"Reuse an accepted route when compatible; disable to plan afresh on subsequent calculations"; onClicked:panel.updateSetting("use_warm_start",checked) }
        NumericSetting { propertyReference: ({target:panel.curve.id,path:["engine_settings","samples"]}); objectName: "routingSamples"; label: "Preferred samples"; decimals: 0; value: panel.settings.samples || 64; enabled: !panel.topologyLocked; hint: "Preferred evaluated point count. Routing adds samples when needed to preserve obstacle-avoiding bends and authored points. Your setting stays unchanged."; onEdited: value=>panel.updateSetting("samples",Math.round(value)) }
        NumericSetting { propertyReference: ({target:panel.curve.id,path:["engine_settings","length_weight"]}); label:"Length weight"; decimals:3; value:panel.settings.length_weight === undefined ? 0.9 : panel.settings.length_weight; hint:"Path-shortening objective weight; zero keeps fidelity and collision constraints active."; onEdited: value=>panel.updateSetting("length_weight",value) }
        NumericSetting { propertyReference: ({target:panel.curve.id,path:["engine_settings","checkpoint_steps"]}); label:"Checkpoint steps"; decimals:0; value:panel.settings.checkpoint_steps || 1; hint:"Solver trials between native checkpoints, separate from the total iteration budget. Larger values can delay cancellation; inspection retains every step."; onEdited: value=>panel.updateSetting("checkpoint_steps",Math.round(value)) }
        NumericSetting { propertyReference: ({target:panel.curve.id,path:["engine_settings","accepted_steps"]}); label: "Iteration budget"; decimals: 0; value: panel.settings.accepted_steps || 24; hint: "Maximum accepted optimization updates. Rejected trials may also run; this is not a time limit."; onEdited: value=>panel.updateSetting("accepted_steps",Math.round(value)) }
    }
}
