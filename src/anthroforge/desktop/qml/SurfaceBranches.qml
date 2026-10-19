import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiSection {
    id: panel
    required property var item
    property var selected: []
    readonly property var boundaries: {
        const revision=workspace.state.revision;
        return expanded && item.id ? workspace.surfaceOptions(item.id,"").boundaries : [];
    }
    readonly property var candidates: {
        const revision=workspace.state.revision;
        return expanded && item.id ? workspace.surfaceOptions(item.id,boundary.currentValue || "").candidates : [];
    }
    title: "Branches"; expanded: false; visible: item.kind !== "PATCH"
    hint: "Join branch endpoints to interior points of an outer main curve first. Choose at least two connected curves in their root order."
    onCandidatesChanged: selected=selected.filter(id=>candidates.some(c=>c.id===id))
    UiCombo { id: boundary; objectName: "branchBoundary"; Layout.fillWidth: true; model: panel.boundaries; textRole: "name"; valueRole: "id"; hint: "Outer main curve" }
    Label { visible: panel.candidates.length===0; text: "No connected branch curves"; color: Theme.muted }
    Repeater {
        model: panel.candidates
        UiCheck {
            required property var modelData
            required property int index
            objectName: "branchSource"+index; text: modelData.name
            checked: panel.selected.includes(modelData.id)
            onClicked: panel.selected=checked ? panel.selected.concat([modelData.id]) : panel.selected.filter(id=>id!==modelData.id)
        }
    }
    UiButton {
        objectName: "addSurfaceBranch"; text: "Add branch"; enabled: panel.selected.length>=2; Layout.fillWidth: true
        onClicked: {
            const sources=panel.candidates.filter(c=>panel.selected.includes(c.id)).map(c=>c.id);
            const use=panel.item.uses.find(u=>u.curve===boundary.currentValue);
            workspace.run("surface.branch.add",{target:panel.item.id,boundary:boundary.currentValue,curves:use.reverse?sources.reverse():sources});
        }
    }
    Repeater {
        model: panel.item.branches || []
        RowLayout {
            required property var modelData
            required property int index
            Label { Layout.fillWidth: true; text: "Branch "+(index+1)+" · "+modelData.curves.length+" curves"; color: Theme.text }
            UiButton { objectName: "removeSurfaceBranch"+index; text: "Remove"; onClicked: workspace.run("surface.branch.remove",{target:panel.item.id,branch:modelData.id}) }
        }
    }
}
