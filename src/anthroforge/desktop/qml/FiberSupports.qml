import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    objectName:"fiberSupportPolicy"
    required property var curve
    readonly property var policy: curve.support_policy || ({automatic:true,included:[],excluded:[]})
    readonly property var rows: (policy.included || []).map(r=>Object.assign({mode:"included"},r)).concat((policy.excluded || []).map(r=>Object.assign({mode:"excluded"},r)))
    visible: curve.bindings !== undefined
    Layout.fillWidth: true; spacing: Theme.gap
    function references(rows) { return (rows || []).map(r=>({target:r.target,role:r.role})); }
    function update(changes) {
        const values=Object.assign({automatic:policy.automatic,included:policy.included,excluded:policy.excluded},changes);
        values.included=references(values.included); values.excluded=references(values.excluded);
        App.runtime.run("fiber.supports.configure", {curve:curve.id,policy:values});
    }
    function override(mode) {
        const ref={target:choice.current.id,role:choice.current.role};
        const keep=r=>r.target!==ref.target || r.role!==ref.role;
        const changes={included:(policy.included || []).filter(keep),excluded:(policy.excluded || []).filter(keep)};
        changes[mode].push(ref); update(changes);
    }
    function remove(row) { const changes={}; changes[row.mode]=policy[row.mode].filter(r=>r.target!==row.target || r.role!==row.role); update(changes); }
    Label { text:"Deformation supports"; color:Theme.muted }
    UiButton { objectName:"fiberRebindAll"; text:"Rebind all points"; hint:"Recapture current positions on their existing targets"; onClicked:App.runtime.run("fiber.rebind",{curve:panel.curve.id}) }
    UiButton { objectName:"fiberReviewPins"; text:"Review pin repairs"; onClicked:App.issuePanel.reviewPins(panel.curve.id) }
    UiCheck { objectName:"fiberSupportsAutomatic"; text:"Automatic supports"; checked:panel.policy.automatic; onClicked:panel.update({automatic:checked}); hint:"Extra surfaces that deform the Fiber; routing obstacles are configured separately" }
    SurfaceSelector { id:choice; Layout.fillWidth:true }
    RowLayout {
        Layout.fillWidth:true
        UiButton { text:"Include"; enabled:!!choice.current.ready; onClicked:panel.override("included") }
        UiButton { text:"Exclude"; enabled:!!choice.current.ready; onClicked:panel.override("excluded") }
    }
    ListView {
        Layout.fillWidth:true; Layout.preferredHeight:Math.min(contentHeight,180)
        clip:true; model:panel.rows; ScrollBar.vertical:ScrollBar {}
        delegate:RowLayout {
            required property var modelData
            width:ListView.view.width; spacing:Theme.gap
            Label { Layout.fillWidth:true; text:modelData.mode+" · "+modelData.target+" · "+modelData.role; elide:Text.ElideMiddle; color:Theme.muted; ToolTip.visible:hovered.hovered; ToolTip.text:text; HoverHandler { id:hovered } }
            UiButton { text:"Remove"; onClicked:panel.remove(modelData) }
        }
    }
}
