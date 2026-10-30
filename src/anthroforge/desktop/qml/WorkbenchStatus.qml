import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: bar
    required property var windowState
    signal detailsRequested()
    color:Theme.panel; implicitHeight:36
    RowLayout {
        anchors.fill:parent; anchors.leftMargin:8; anchors.rightMargin:8; spacing:6
        UiButton { objectName:"activityToggle"; text:"Activity"+(bar.windowState.activeJobCount ? " ("+bar.windowState.activeJobCount+")" : ""); Layout.preferredWidth:100; flatStyle:true; checked:bar.windowState.activityOpen; onClicked:{ bar.windowState.activityOpen=!bar.windowState.activityOpen; if(bar.windowState.activityOpen) bar.windowState.issuesOpen=false; } }
        UiButton { objectName:"issuesToggle"; text:"Issues ("+(App.issuePanel.state.count || 0)+")"; Layout.preferredWidth:90; flatStyle:true; checked:bar.windowState.issuesOpen; hint:App.issuePanel.state.summary || "Review issues and suggested repairs"; onClicked:{ bar.windowState.issuesOpen=!bar.windowState.issuesOpen; if(bar.windowState.issuesOpen) bar.windowState.activityOpen=false; } }
        UiCheck { objectName:"attachmentsEnabled"; text:"Attachments"; checked:App.runtime.state.attachments; enabled:!App.runtime.state.waiting; onClicked:App.runtime.run("attachments.enable",{enabled:checked}) }
        Label { text:"Update"; color:Theme.muted }
        UiEnumCombo { objectName:"projectUpdateMode"; Layout.preferredWidth:110; codes:["LIVE","ON_RELEASE","MANUAL"]; value:App.runtime.state.mode; hint:"Choose when dependent geometry updates"; onChosen:code=>App.runtime.run("update_mode",{mode:code}) }
        UiButton { objectName:"recalculate"; text:"Recalculate"; hint:"Update pending geometry"; enabled:!App.runtime.state.waiting; onClicked:App.runtime.run("evaluate",{}) }
        Label { text:bar.windowState.activeJobCount ? "Calculating…" : bar.windowState.jobFailed ? "Calculation failed" : "Idle"; color:bar.windowState.jobFailed ? Theme.danger : Theme.muted; Layout.fillWidth:true; elide:Text.ElideRight }
        UiButton { objectName:"operationDetails"; text:"Details"; flatStyle:true; enabled:!!App.runtime.state.message; hint:App.runtime.state.message || "Last operation"; onClicked:bar.detailsRequested() }
        Label {
            text:App.runtime.state.dirty ? "Unsaved" : "Saved"; color:App.runtime.state.dirty ? Theme.accent : Theme.muted; Layout.preferredWidth:50
            HoverHandler { id:saveHover }
            ToolTip.visible:saveHover.hovered; ToolTip.delay:500
            ToolTip.text:App.runtime.state.object_count+" objects · Revision "+App.runtime.state.revision+"\nDisplay units: "+App.runtime.state.display_units
        }
    }
}
