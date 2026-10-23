import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiSection {
    id: inspector
    required property var adapter
    title: "Inspect shortcut"
    expanded: adapter.opened
    onExpandedChanged: adapter.activate(expanded && visible)
    onVisibleChanged: adapter.activate(expanded && visible)
    ShortcutDetail { label: "Update"; value: inspector.adapter.state.status || "Unavailable" }
    UiCheck { objectName: "shortcutShowEffects"; text: "Show effects"; checked: !!inspector.adapter.state.showEffects; onClicked: inspector.adapter.showEffects(checked) }
    Label { visible: !!inspector.adapter.state.showEffects; text: "Gold: direct · Cyan: downstream\nGreen: authored anchors · Pink: effective anchors"; color: Theme.muted; wrapMode: Text.Wrap; Layout.fillWidth: true; font.pixelSize: 10 }
    UiSection {
        title: "Affected anatomy"; expanded: true
        UiField { Layout.fillWidth: true; placeholderText: "Search affected objects and outputs"; onTextChanged: inspector.adapter.filter(text) }
        ListView {
            objectName: "shortcutEffectList"; Layout.fillWidth: true; Layout.preferredHeight: 180
            model: inspector.adapter.affected; clip: true; ScrollBar.vertical: ScrollBar { policy: ScrollBar.AlwaysOn }
            delegate: ColumnLayout {
                required property string label
                required property string detail
                required property string target
                width: ListView.view.width-14; height: 52; spacing: 0
                RowLayout {
                    Layout.fillWidth: true
                    Label { text: label; color: Theme.text; elide: Text.ElideMiddle; Layout.fillWidth: true }
                    UiButton { glyph: "frame"; hint: "Navigate to object or driver"; onClicked: inspector.adapter.navigate(target,true) }
                }
                Label { text: detail; elide: Text.ElideRight; color: Theme.muted; font.pixelSize: 10; Layout.fillWidth: true; ToolTip.text: detail; ToolTip.visible: hovered.hovered; HoverHandler { id: hovered } }
            }
        }
        RowLayout {
            UiButton { text: "‹"; enabled: (inspector.adapter.state.offset || 0)>0; onClicked: inspector.adapter.page(-1) }
            Label { text: String(inspector.adapter.state.total || 0)+" potential outputs"; color: Theme.muted; Layout.fillWidth: true }
            UiButton { text: "›"; enabled: (inspector.adapter.state.offset || 0)+50<(inspector.adapter.state.total || 0); onClicked: inspector.adapter.page(1) }
        }
    }
    UiSection {
        title: "Formula values"; expanded: false
        ListView {
            objectName: "shortcutFormulaEvidence"; Layout.fillWidth: true; Layout.preferredHeight: 240
            model: inspector.adapter.state.formulas || []; clip: true; ScrollBar.vertical: ScrollBar { policy: ScrollBar.AlwaysOn }
            delegate: ShortcutFormulaEvidence { required property var modelData; value: modelData; adapter: inspector.adapter; width: ListView.view.width-14 }
        }
    }
    UiSection {
        title: "Attachment effects"; expanded: false
        ShortcutDetail { label: "Policy"; value: inspector.adapter.state.policy?.captured ? "Captured for the active edit" : "Prospective · no temporary anchors" }
        ShortcutDetail { label: "Backsolve"; value: inspector.adapter.state.policy?.policy?.backsolve ? "Preserve owner anchor by translation" : "Off · existing bindings still retained" }
        ListView {
            Layout.fillWidth: true; Layout.preferredHeight: 180; clip: true
            model: inspector.adapter.state.policy?.rows || []; ScrollBar.vertical: ScrollBar { policy: ScrollBar.AlwaysOn }
            delegate: ColumnLayout {
                required property var modelData
                width: ListView.view.width-14; height: 145; spacing: 2
                Label { text: modelData.name; color: Theme.text; elide: Text.ElideMiddle; Layout.fillWidth: true }
                ShortcutDetail { label: "Authored"; value: [modelData.authored.parent_mode,modelData.authored.child_mode,modelData.authored.follow_rotation ? "Follow rotation" : "No rotation",modelData.authored.strategy].join(" · ") }
                ShortcutDetail { label: "Override"; value: modelData.override ? [modelData.override.parent_anchor,modelData.override.child_anchor,modelData.override.follow_rotation,modelData.override.strategy].join(" · ") : "Keep authored settings" }
                ShortcutDetail { label: "Binding"; value: modelData.effective ? "Effective binding captured" : modelData.binding_available ? "Authored binding retained" : "No authored binding" }
                ShortcutDetail { label: "Effective"; value: modelData.effective ? [modelData.effective.parent_mode,modelData.effective.child_mode,modelData.effective.follow_rotation ? "Follow rotation" : "No rotation",modelData.effective.strategy].join(" · ") : "Unavailable until captured" }
                UiButton { text: "Locate"; onClicked: inspector.adapter.navigate(modelData.target,true) }
            }
        }
    }
    UiSection {
        title: "Update details"; expanded: false
        ShortcutDetail { label: "Published"; value: String(inspector.adapter.state.progress?.updated_outputs || 0)+" outputs · not a count of spatial changes" }
        ShortcutDetail { label: "Jobs"; value: (inspector.adapter.state.progress?.jobs || []).map(job => job.label+" · "+job.state).join("; ") || "No related active jobs" }
        ShortcutDetail { label: "Failure"; value: (inspector.adapter.state.progress?.failures || []).join("; ") || "None" }
        ListView {
            Layout.fillWidth: true; Layout.preferredHeight: 160; clip: true
            model: inspector.adapter.state.progress?.blockers || []; ScrollBar.vertical: ScrollBar { policy: ScrollBar.AlwaysOn }
            delegate: ColumnLayout {
                required property var modelData
                width: ListView.view.width-14; height: 56
                Label { text: modelData.name+" · "+modelData.output; color: Theme.text; elide: Text.ElideMiddle; Layout.fillWidth: true }
                Label { text: modelData.error || (modelData.blocked ? "Blocked dependency" : modelData.update_mode+" · "+modelData.status); color: Theme.muted; elide: Text.ElideRight; Layout.fillWidth: true }
                TapHandler { onTapped: inspector.adapter.navigate(modelData.owner,false) }
            }
        }
    }
}
