import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    required property var curve
    property var chosen: []
    property int count: 64
    readonly property var preview: workspace.conversionState
    readonly property bool ours: preview.target === (curve.id || "")
    readonly property bool routed: engine.currentText === "ROUTED"
    readonly property bool running: ours && ["queued","running"].includes(preview.state)
    Layout.fillWidth: true; spacing: Theme.gap
    function requestPreview() {
        const args={curve:curve.id,engine:engine.currentText,samples:count};
        args.mode=routed || sampling.currentIndex===1 ? "AUTHORED" : "EVALUATED";
        if(routed) args.points=chosen;
        workspace.run("curve.conversion.preview",args);
    }
    UiButton { id: expand; text: "Change path engine"; checkable: true; Layout.fillWidth: true }
    ColumnLayout {
        visible: expand.checked; Layout.fillWidth: true; spacing: Theme.gap
        UiCombo { id: engine; model: ["BEZIER","POLYLINE","ROUTED"]; Layout.fillWidth: true }
        UiCombo { id: sampling; visible: !panel.routed; model: ["Sample accepted shape","Keep authored points"]; Layout.fillWidth: true }
        NumericSetting { visible: !panel.routed && sampling.currentIndex===0; label: "Conversion points"; decimals: 0; value: panel.count; onEdited: value=>panel.count=Math.max(3,Math.min(4096,Math.round(value))) }
        Label { visible: panel.routed; text: "Choose structural routing points, including open endpoints."; color: Theme.muted; wrapMode: Text.WordWrap; Layout.fillWidth: true }
        Repeater {
            model: panel.routed ? (panel.curve.points || []) : []
            UiCheck {
                required property var modelData; required property int index
                text: "Point "+(index+1); checked: panel.chosen.includes(modelData.id)
                onClicked: panel.chosen=checked ? panel.chosen.concat([modelData.id]) : panel.chosen.filter(id=>id!==modelData.id)
            }
        }
        UiButton { objectName: "previewCurveConversion"; text: panel.running ? "Rebuild preview" : "Preview conversion"; Layout.fillWidth: true; enabled: !!panel.curve.id; onClicked: panel.requestPreview() }
        Label { visible: panel.ours; text: panel.preview.error || (panel.preview.state==="ready" ? "Green preview · "+panel.preview.points+" authored points" : panel.preview.state); color: Theme.muted; wrapMode: Text.WordWrap; Layout.fillWidth: true }
        RowLayout {
            visible: panel.ours
            UiButton { objectName: "acceptCurveConversion"; text: "Accept"; enabled: panel.preview.state==="ready"; onClicked: workspace.run("curve.conversion.accept",{token:panel.preview.token}) }
            UiButton { text: "Cancel preview"; onClicked: workspace.run("curve.conversion.cancel",{}) }
        }
    }
}
