import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    required property var contributor
    readonly property var settings: contributor.settings || ({})
    readonly property var budget: contributor.budget || ({})
    signal editDocumentBudget()
    visible: !!contributor.scp || !!contributor.flow_available
    enabled: !!contributor.editable
    Layout.fillWidth: true
    spacing: Theme.gap
    function change(key, value) {
        const values = {}; values[key] = value;
        App.runtime.run("skin.contributor.configure", {owner:contributor.owner, values:values});
    }
    Label {
        text: (panel.contributor.scp ? "Subtree: " : "Topology guide: ") + (panel.contributor.name || "")
        color:Theme.text; font.bold:true; Layout.fillWidth:true; wrapMode:Text.Wrap
    }
    UiCheck {
        objectName:"skinFiberFlow"; visible:!!panel.contributor.flow_available
        text:"Use as topology FLOW guide"; checked:!!panel.settings.flow
        onToggled:panel.change("flow", checked)
    }
    ColumnLayout {
        visible:!!panel.contributor.scp; Layout.fillWidth:true
        UiCombo {
            objectName:"skinSourceDensityMode"; Layout.fillWidth:true
            model:["Inherit topology budget", "Set subtree budget"]
            currentIndex:panel.settings.density_mode === "SUBTREE_BUDGET" ? 1 : 0
            onActivated:panel.change("density_mode", currentIndex ? "SUBTREE_BUDGET" : "INHERIT")
        }
        NumericSetting {
            objectName:"skinSubtreeQuads"; label:"Subtree target quads"
            minimum:100; maximum:500000; decimals:0
            visible:panel.settings.density_mode === "SUBTREE_BUDGET"
            value:panel.settings.target_quads || 1000
            onEdited:value=>panel.change("target_quads", Math.round(value))
        }
        Label {
            objectName:"skinParentBudget"
            text:"Enclosing budget: " + (panel.budget.name || "Document") + " · " + (panel.budget.target_quads || 0) + " quads"
            color:Theme.muted; Layout.fillWidth:true; wrapMode:Text.Wrap
            ToolTip.visible:budgetHover.hovered
            ToolTip.text:"Shared by this subtree and its siblings. This budget controls topology, not Draft triangles."
            HoverHandler { id:budgetHover }
        }
        UiButton {
            objectName:"skinEditParentBudget"; Layout.fillWidth:true
            text:panel.budget.owner ? "Select " + panel.budget.name + " to edit budget" : "Edit document budget"
            onClicked:panel.budget.owner ? App.selection.select(panel.budget.owner) : panel.editDocumentBudget()
        }
        Label {
            visible:!!(panel.contributor.budget_errors || []).length
            text:(panel.contributor.budget_errors || []).join("\n")
            color:Theme.muted; Layout.fillWidth:true; wrapMode:Text.Wrap
        }
    }
    Label { visible:!!panel.contributor.reason; text:panel.contributor.reason || ""; color:Theme.muted; Layout.fillWidth:true; wrapMode:Text.Wrap }
}
