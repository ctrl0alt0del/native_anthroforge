import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    required property var curve
    property var selected: []
    property string checkboxName: "routingObstacle"
    readonly property var automatic: [...new Set((curve.supports || []).concat((curve.bindings || []).map(b=>b.target)))]
    readonly property var effective: [...new Set(selected.concat(automatic))]
    readonly property var surfaces: { const revision=workspace.state.revision; return workspace.anatomicalSurfaces(); }
    signal edited(var values)
    Layout.fillWidth: true; spacing: Theme.gap
    UiButton { id: expand; objectName: panel.checkboxName+"Toggle"; text: "Routing obstacles · "+panel.effective.length; checkable: true; Layout.fillWidth: true }
    Label {
        objectName: panel.checkboxName+"Notice"
        visible: panel.effective.length===0
        text: "No obstacles selected. The path ignores SCP geometry."
        color: Theme.accent; wrapMode: Text.WordWrap; Layout.fillWidth: true
    }
    ColumnLayout {
        visible: expand.checked; Layout.fillWidth: true
        Label { text: "Choose surfaces to avoid. Fiber attachment surfaces are automatic."; color: Theme.muted; wrapMode: Text.WordWrap; Layout.fillWidth: true }
        Repeater {
            model: panel.surfaces
            UiCheck {
                required property var modelData
                objectName: panel.checkboxName
                property string targetId: modelData.id
                readonly property bool automatic: panel.automatic.includes(targetId)
                text: modelData.name+(automatic ? " · attachment" : "")
                checked: panel.effective.includes(targetId); enabled: !automatic
                onClicked: panel.edited(checked ? panel.selected.concat([targetId]) : panel.selected.filter(key=>key!==targetId))
            }
        }
    }
}
