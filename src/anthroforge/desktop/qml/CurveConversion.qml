import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "RoutingOptions.js" as RoutingOptions

ColumnLayout {
    id: panel
    objectName: "curveConversion"
    required property var curve
    property var chosen: []
    property var obstacleSettings: ({obstacle_mode:"AUTO",excluded_obstacles:[],obstacles:[]})
    property var sourcePoints: []
    property string sourceId: ""
    property string sourceEngine: ""
    property int count: 64
    readonly property var preview: workspace.conversionState
    readonly property bool ours: preview.target === (curve.id || "")
    readonly property bool routed: engine.currentText === "ROUTED"
    readonly property bool running: ours && ["queued","running"].includes(preview.state)
    readonly property bool expanded: expand.checked
    readonly property var authoredPoints: curve.points || []
    readonly property string activeEngine: curve.engine || ""
    readonly property var pointRows: { const revision=workspace.state.revision; return workspace.conversionPoints(curve.id || "").map(r=>Object.assign({},r,{chosen:r.locked || chosen.includes(r.key)})); }
    Layout.fillWidth: true; spacing: Theme.gap
    onCurveChanged: synchronizeSource()
    onAuthoredPointsChanged: synchronizeSource()
    onActiveEngineChanged: synchronizeEngine()
    Component.onCompleted: synchronizeSource()
    function synchronizeEngine() {
        if(!engine) return;
        if(sourceId!==(curve.id || "") || sourceEngine!==activeEngine) {
            sourceEngine=activeEngine;
            engine.currentIndex=Math.max(0,engine.model.indexOf(sourceEngine));
        }
    }
    function synchronizeSource() {
        synchronizeEngine();
        const ids=authoredPoints.map(p=>p.id);
        if(sourceId!==(curve.id || "")) {
            sourceId=curve.id || ""; chosen=ids;
            obstacleSettings=curve.engine==="ROUTED" ? RoutingOptions.copy(curve.engine_settings) : {obstacle_mode:"AUTO",excluded_obstacles:[],obstacles:[]};
        } else chosen=ids.filter(id=>chosen.includes(id) || !sourcePoints.includes(id));
        sourcePoints=ids;
    }
    function requestPreview() {
        const args={curve:curve.id,engine:engine.currentText,samples:count};
        args.mode=routed || sampling.currentIndex===1 ? "AUTHORED" : "EVALUATED";
        if(routed) {
            args.points=pointRows.filter(r=>r.chosen).map(r=>r.key);
            args.settings=Object.assign({},obstacleSettings);
            if(curve.engine==="ROUTED")
                ["samples","radius","accepted_steps"].forEach(key=>args.settings[key]=curve.engine_settings[key]);
            args.settings.samples=Math.max(args.settings.samples || count,args.points.length);
        }
        workspace.run("curve.conversion.preview",args);
    }
    UiButton { id: expand; objectName: "curveConversionToggle"; text: "Change path engine"; checkable: true; Layout.fillWidth: true }
    ColumnLayout {
        visible: expand.checked; Layout.fillWidth: true; spacing: Theme.gap
        Label { text: "Convert to"; color: Theme.muted }
        UiCombo { id: engine; objectName: "conversionEngine"; model: ["BEZIER","POLYLINE","ROUTED"]; hint: "Conversion target. Preview and apply to change the active engine."; Layout.fillWidth: true }
        Label {
            objectName: "conversionEngineStatus"
            text: engine.currentText!==panel.curve.engine ? engine.currentText+" is not active. Preview, then apply below." : "Preview changes before applying."
            color: engine.currentText!==panel.curve.engine ? Theme.accent : Theme.muted
            wrapMode: Text.WordWrap; Layout.fillWidth: true
        }
        UiCombo { id: sampling; visible: !panel.routed; model: ["Sample accepted shape","Keep authored points"]; Layout.fillWidth: true }
        NumericSetting { visible: !panel.routed && sampling.currentIndex===0; label: "Conversion points"; decimals: 0; value: panel.count; onEdited: value=>panel.count=Math.max(3,Math.min(4096,Math.round(value))) }
        RoutingObstacles { visible: panel.routed; curve: panel.curve; settings: panel.obstacleSettings; editorName: "conversionObstacle"; onEdited: values=>panel.obstacleSettings=values }
        ChoiceEditor {
            visible: panel.routed; objectName: "conversionPoint"; title: "Authored routing points"; rows: panel.pointRows
            chosenLabel: "Retained"; otherLabel: "Omitted"; chooseLabel: "Keep shown"; clearLabel: "Omit shown"; resetLabel: "Keep all authored points"
            summary: choices.counts.chosen+" / "+choices.counts.total+" retained"
            onEdited: values=>panel.chosen=values
            onResetRequested: panel.chosen=panel.sourcePoints.slice()
            onFocused: key=>authoring.focusCurvePoint(panel.curve.id,key)
        }
        UiButton { objectName: "previewCurveConversion"; text: panel.running ? "Rebuild preview" : "Preview conversion"; Layout.fillWidth: true; enabled: !!panel.curve.id; onClicked: panel.requestPreview() }
        Label { objectName: "conversionPreviewStatus"; visible: panel.ours; text: panel.preview.error || (panel.preview.state==="ready" ? panel.preview.engine+" preview ready · not applied" : panel.preview.state); color: Theme.muted; wrapMode: Text.WordWrap; Layout.fillWidth: true }
        RowLayout {
            visible: panel.ours
            UiButton { objectName: "acceptCurveConversion"; text: panel.preview.engine ? "Use "+panel.preview.engine : "Apply preview"; enabled: panel.preview.state==="ready"; onClicked: workspace.run("curve.conversion.accept",{token:panel.preview.token}) }
            UiButton { text: "Cancel preview"; onClicked: workspace.run("curve.conversion.cancel",{}) }
        }
    }
}
