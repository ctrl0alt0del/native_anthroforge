import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    required property var curve
    readonly property var surfaces: { const revision=workspace.state.revision; return workspace.anatomicalSurfaces(); }
    Layout.fillWidth: true; spacing: Theme.gap
    function createFiber() {
        const bindings=[];
        for(let i=0;i<anchorRows.count;i++) {
            const row=anchorRows.itemAt(i);
            if(row.bound) bindings.push({point:row.pointId,target:row.targetId});
        }
        workspace.run("fiber.create",{curve:curve.id,bindings:bindings,name:fiberName.text});
    }
    UiButton { id: expand; text: "Create fiber from curve"; checkable: true; Layout.fillWidth: true; enabled: !!panel.curve.id }
    ColumnLayout {
        visible: expand.checked; Layout.fillWidth: true; spacing: Theme.gap
        UiField { id: fiberName; text: "Fiber"; Layout.fillWidth: true; Accessible.name: "New fiber name" }
        Label { text: panel.curve.closed ? "Choose at least one anchor." : "Both endpoints require a surface."; color: Theme.muted }
        Repeater {
            id: anchorRows; model: panel.curve.points || []
            RowLayout {
                required property var modelData; required property int index
                readonly property bool mandatory: !panel.curve.closed && (index===0 || index===anchorRows.count-1)
                readonly property bool bound: chosen.checked
                readonly property string pointId: modelData.id
                readonly property string targetId: target.currentValue || ""
                Layout.fillWidth: true
                UiCheck { id: chosen; text: "Point "+(index+1); checked: parent.mandatory || (panel.curve.closed && index===0); enabled: !parent.mandatory }
                UiCombo { id: target; Layout.fillWidth: true; model: panel.surfaces; textRole: "name"; valueRole: "id"; enabled: chosen.checked; hint: "Anatomical attachment surface" }
            }
        }
        UiButton { objectName: "createFiberFromCurve"; property string sourceId: panel.curve.id || ""; text: "Create independent fiber"; Layout.fillWidth: true; enabled: panel.surfaces.length>0 && !!sourceId; onClicked: panel.createFiber() }
    }
}
