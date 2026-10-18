import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    readonly property var service: workspace.issuePanel
    spacing: 6
    function filterRows() { service.filter(search.text, ["","error","warning","info"][severity.currentIndex], dismissed.checked); }
    GridLayout {
        columns: panel.width < 660 ? 3 : 5
        Layout.fillWidth: true
        UiField { id: search; objectName: "issueSearch"; Layout.fillWidth: true; Layout.columnSpan: panel.width < 660 ? 2 : 1; placeholderText: "Search issues…"; onTextChanged: panel.filterRows() }
        UiCombo { id: severity; objectName: "issueSeverity"; implicitWidth: 125; model: ["All severities","Errors","Warnings","Information"]; onActivated: panel.filterRows() }
        UiCheck { id: dismissed; objectName: "issueShowDismissed"; text: "Dismissed"; onClicked: panel.filterRows() }
        UiButton { objectName: "issueRecheckAll"; text: "Recheck"; hint: "Run available checks without changing geometry"; onClicked: panel.service.run("issues.recheck",{}) }
        UiButton { objectName: "issueCancelChecks"; text: "Cancel"; hint: "Cancel running checks"; enabled: !panel.service.state.complete; onClicked: panel.service.run("issues.cancel",{}) }
    }
    Label { Layout.fillWidth: true; text: panel.service.state.summary || "Not checked"; color: panel.service.state.complete ? Theme.muted : Theme.accent; elide: Text.ElideRight; ToolTip.visible: statusHover.hovered; ToolTip.text: text; HoverHandler { id: statusHover } }
    SplitView {
        Layout.fillWidth: true; Layout.fillHeight: true
        handle: Rectangle { implicitWidth: 4; color: Theme.border }
        ListView {
            id: list; objectName: "issueList"; clip: true
            SplitView.preferredWidth: 360; SplitView.minimumWidth: 180
            model: panel.service.issueModel
            spacing: 3
            delegate: ItemDelegate {
                id: row
                required property string issueId
                required property string summary
                required property string severity
                required property string targetLabel
                required property string freshness
                required property bool dismissed
                required property string code
                objectName: "issueRow-"+row.issueId
                width: ListView.view.width; height: 47
                highlighted: panel.service.detail.id === row.issueId
                onClicked: panel.service.selectIssue(row.issueId)
                contentItem: Column {
                    Label { width: parent.width; text: row.summary; color: row.severity === "error" ? Theme.danger : row.severity === "warning" ? Theme.accent : Theme.text; elide: Text.ElideRight }
                    Label { width: parent.width; text: row.targetLabel+" · "+row.freshness+(row.dismissed ? " · dismissed" : ""); color: Theme.muted; font.pixelSize: 10; elide: Text.ElideRight }
                }
                background: Rectangle { color: row.highlighted ? Theme.selection : row.hovered ? Theme.field : "transparent"; radius: 3 }
            }
            ScrollBar.vertical: ScrollBar {}
            Label { anchors.centerIn: parent; visible: list.count === 0; text: "No matching issues"; color: Theme.muted }
        }
        IssueDetails { SplitView.fillWidth: true; SplitView.minimumWidth: 240; service: panel.service }
    }
    RowLayout {
        Label { Layout.fillWidth: true; text: panel.service.state.total + " matching · " + panel.service.state.count + " total"; color: Theme.muted; font.pixelSize: 10 }
        UiButton { text: "Previous"; enabled: panel.service.state.offset > 0; onClicked: panel.service.page(-1) }
        UiButton { text: "Next"; enabled: panel.service.state.offset+100 < panel.service.state.total; onClicked: panel.service.page(1) }
    }
}
