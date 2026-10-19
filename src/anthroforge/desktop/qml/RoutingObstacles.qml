import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "RoutingOptions.js" as RoutingOptions

ColumnLayout {
    id: panel
    required property var curve
    property var settings: ({obstacle_mode:"AUTO", excluded_obstacles:[], obstacles:[]})
    property string editorName: "routingObstacle"
    readonly property bool automatic: (settings.obstacle_mode || "AUTO")==="AUTO"
    readonly property var options: RoutingOptions.copy(settings)
    readonly property var rows: { const revision=workspace.state.revision; return workspace.routingChoices(curve.id || "",options); }
    signal edited(var settings)
    Layout.fillWidth: true; spacing: Theme.gap
    function update(values) {
        const editable=rows.filter(r=>!r.locked).map(r=>r.key);
        const changes=RoutingOptions.copy(settings);
        changes[automatic ? "excluded_obstacles" : "obstacles"]=values.filter(key=>editable.includes(key));
        panel.edited(changes);
    }
    UiCombo {
        objectName: panel.editorName+"Mode"; Layout.fillWidth: true
        model: ["Automatic obstacles","Manual obstacle list"]
        currentIndex: panel.automatic ? 0 : 1
        hint: "Automatic considers all SCP surfaces, independent of visibility and workspace. Optional exclusions are below."
        onActivated: panel.edited(Object.assign({},panel.options,{obstacle_mode:currentIndex===0 ? "AUTO" : "MANUAL"}))
    }
    ChoiceEditor {
        objectName: panel.editorName; rows: panel.rows
        title: panel.automatic ? "Obstacle exclusions" : "Obstacle selection"
        chosenLabel: panel.automatic ? "Excluded" : "Included"; otherLabel: panel.automatic ? "Included" : "Excluded"
        chooseLabel: panel.automatic ? "Exclude shown" : "Include shown"; clearLabel: panel.automatic ? "Restore shown" : "Exclude shown"
        resetLabel: panel.automatic ? "Restore automatic obstacles" : "Clear manual selection"
        summary: panel.automatic ? (choices.counts.total-choices.counts.chosen)+" included · "+choices.counts.chosen+" excluded" : choices.counts.chosen+" / "+choices.counts.total+" included"
        onEdited: values=>panel.update(values)
        onResetRequested: panel.update([])
    }
    Label {
        objectName: panel.editorName+"Notice"
        visible: !panel.automatic && !panel.rows.some(r=>r.chosen)
        text: "No obstacles included. The path ignores SCP geometry."
        color: Theme.accent; wrapMode: Text.WordWrap; Layout.fillWidth: true
    }
}
