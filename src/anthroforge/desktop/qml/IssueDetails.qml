import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiScrollView {
    id: panel
    objectName: "issueDetails"
    required property var service
    readonly property var issue: service.detail
    clip: true; leftPadding: Theme.inset
    contentWidth: availableWidth
    ColumnLayout {
        width: panel.availableWidth; spacing: Theme.gap
        Label { Layout.fillWidth: true; text: panel.issue.summary || "Select an issue to inspect its evidence"; color: Theme.text; font.bold: true; wrapMode: Text.Wrap; maximumLineCount: 3; elide: Text.ElideRight }
        Flow {
            Layout.fillWidth: true; spacing: 5
            UiButton { objectName: "issueSelectTarget"; text: "Select target"; visible: !!panel.issue.target; enabled: panel.service.state.canNavigate; onClicked: panel.service.navigate(panel.issue.target,false) }
            UiButton { objectName: "issueFrameTarget"; text: "Frame target"; visible: !!panel.issue.target; enabled: panel.service.state.canNavigate; onClicked: panel.service.navigate(panel.issue.target,true) }
            UiButton { objectName: "issueRecheck"; text: "Recheck provider"; visible: !!panel.issue.id; onClicked: panel.service.run("issues.recheck",{provider:panel.issue.provider}) }
            UiButton { objectName: "issueDismiss"; text: panel.issue.dismissed ? "Restore" : "Dismiss"; visible: !!panel.issue.exists; onClicked: panel.service.run("issues.dismiss",{identity:panel.issue.id,dismissed:!panel.issue.dismissed}) }
        }
        Repeater {
            model: panel.issue.fixes || []
            UiButton { required property var modelData; objectName: "issueFix-"+modelData.name; text: modelData.label; enabled: !panel.issue.repairActive; onClicked: panel.service.run("issues.fix",{identity:panel.issue.id,name:modelData.name}) }
        }
        Label { Layout.fillWidth: true; visible: !!panel.issue.repair; text: "Repair: "+(panel.issue.repair || ""); color: Theme.accent; wrapMode: Text.Wrap }
        UiButton { objectName: "issueCancelFix"; text: "Cancel repair"; visible: !!panel.issue.repairActive; onClicked: panel.service.run("issues.cancel_fix",{identity:panel.issue.id}) }
        Repeater {
            model: panel.issue.relatedTargets || []
            UiButton { required property var modelData; text: "Related: "+modelData.label; flatStyle: true; enabled: panel.service.state.canNavigate; onClicked: panel.service.navigate(modelData.id,true) }
        }
        UiSection {
            title: "Details & evidence"; expanded: false; visible: !!panel.issue.id
        Label { Layout.fillWidth: true; visible: !!panel.issue.id; text: (panel.issue.provider || "")+" / "+(panel.issue.stage || "")+" · "+(panel.issue.check_state || ""); color: Theme.muted; wrapMode: Text.Wrap }
        Label { Layout.fillWidth: true; visible: !!panel.issue.details; text: panel.issue.details || ""; color: Theme.text; wrapMode: Text.WrapAnywhere }
            TextArea { objectName: "issueEvidence"; Layout.fillWidth: true; visible: !!panel.issue.id; text: (panel.issue.code || "")+"\n"+(panel.issue.evidenceText || ""); readOnly: true; selectByMouse: true; wrapMode: TextEdit.WrapAnywhere; font.family: "Consolas"; font.pixelSize: 10; color: Theme.muted; background: Rectangle { color: Theme.field; radius: 3 } }
        }
    }
}
