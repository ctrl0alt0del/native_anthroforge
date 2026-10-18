import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiSection {
    id: panel
    required property var curve
    required property var point
    readonly property var info: {
        const revision = workspace.state.revision;
        return expanded && curve.id && point.id ? authoring.junctionOptions(curve.id,point.id) : {};
    }
    readonly property var candidates: info.curves || []
    readonly property var target: candidates[targetCurve.currentIndex] || {}
    readonly property var targetPoints: target.points || []
    title: "Shared junction"; expanded: false; visible: !!point.id
    hint: "Join explicit authored points. The chosen source supplies the accepted position and anatomical binding. Editing either member updates the shared point."
    Label {
        visible: !!panel.info.id; Layout.fillWidth: true; wrapMode: Text.WordWrap
        text: (panel.info.members || []).join(", "); color: Theme.muted
    }
    ColumnLayout {
        visible: !panel.info.id; Layout.fillWidth: true
        UiCombo { id: targetCurve; objectName: "junctionTargetCurve"; Layout.fillWidth: true; model: panel.candidates; textRole: "name"; hint: "Other curve or fiber" }
        UiCombo { id: targetPoint; objectName: "junctionTargetPoint"; Layout.fillWidth: true; model: panel.targetPoints; textRole: "name"; hint: "Authored point to connect" }
        UiCombo { id: source; objectName: "junctionSource"; Layout.fillWidth: true; model: ["Use this point as source", "Use target point as source"]; hint: "A shared anatomical binding requires a bound fiber source" }
        UiButton {
            objectName: "createJunction"; text: "Join points"; Layout.fillWidth: true
            enabled: !!panel.target.id && !!panel.targetPoints[targetPoint.currentIndex]?.id && !panel.targetPoints[targetPoint.currentIndex]?.junction
            onClicked: {
                const here={curve:panel.curve.id,point:panel.point.id};
                const there={curve:panel.target.id,point:panel.targetPoints[targetPoint.currentIndex].id};
                workspace.run("junction.create",{source:source.currentIndex===0?here:there,targets:[source.currentIndex===0?there:here]});
            }
        }
    }
    UiButton { objectName: "removeJunction"; text: "Detach junction"; visible: !!panel.info.id; Layout.fillWidth: true; hint: "Keep each member's current shape and binding"; onClicked: workspace.run("junction.remove",{junction:panel.info.id}) }
}
