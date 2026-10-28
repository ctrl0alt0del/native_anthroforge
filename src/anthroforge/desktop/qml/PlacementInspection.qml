import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiSection {
    id: panel
    title:"Placement & support"; expanded:false; stateKey:"inspect/placement"
    readonly property var tool:workspace.placementInspection
    readonly property var report:tool.state.report || ({})
    readonly property var preview:report.preview || ({})
    readonly property var confirmed:report.confirmed || ({})
    function length(v) { return typeof v==="number" ? (v/workspace.state.unit_factor).toPrecision(5)+" "+workspace.state.display_units : "—"; }
    function vector(v) { return v ? v.map(n=>(n/workspace.state.unit_factor).toFixed(4)).join(", ")+" "+workspace.state.display_units : "—"; }
    UiButton { objectName:"inspectPlacement"; text:panel.tool.state.active ? "Finish placement inspection" : "Explain placement at a surface"; Layout.fillWidth:true; checkable:true; checked:panel.tool.state.active; onClicked:panel.tool.toggle(); hint:"Click a surface to compare the fast preview with confirmed exterior placement. No point or attachment is changed." }
    UiCombo { id:bindingChoice; Layout.fillWidth:true; visible:panel.tool.state.bindings.length>0; model:panel.tool.state.bindings; textRole:"label"; hint:"Inspect the current bound point against its existing support."; onActivated:panel.tool.inspectBinding(model[currentIndex].point) }
    UiButton { text:"Explain selected binding"; Layout.fillWidth:true; visible:panel.tool.state.bindings.length>0; onClicked:panel.tool.inspectBinding(panel.tool.state.bindings[Math.max(0,bindingChoice.currentIndex)].point) }
    UiDetail { label:"Preview"; value:panel.preview.name || "—" }
    UiDetail { label:"Confirmed"; value:panel.confirmed.name || (panel.report.preview ? "No exterior hit" : "—") }
    UiDetail { label:"Preview XYZ"; value:panel.vector(panel.preview.position) }
    UiDetail { label:"Accepted XYZ"; value:panel.vector(panel.confirmed.accepted) }
    UiDetail { label:"Displacement"; value:panel.length(panel.report.displacement?.[3]) }
    UiDetail { label:"Support distance"; value:panel.length(panel.report.support_distance) }
    UiDetail { label:"Approach"; value:panel.confirmed.hit ? (panel.confirmed.approach_cosine < 0 ? "Toward face front" : "From face back or tangent") : "—" }
    UiDetail { label:"Query surface"; value:panel.confirmed.hit ? (panel.confirmed.qualified_copy ? "Exterior copy; original retained" : "Qualified original") : "—" }
    UiDetail { label:"Revision"; value:panel.confirmed.hit ? String(panel.confirmed.revision) : "—" }
    UiHelp { explanation:"This checks placement now, not the original gesture. Yellow lines show the requested ray and candidate faces. A changed candidate identifies which preview face was excluded or superseded; no automatic repair occurs." }
    UiNotice { text:panel.report.error || panel.tool.state.error || (panel.tool.state.state==="stale" ? "Surface changed. Click again for current evidence." : ""); error:true }
    UiButton { text:"Locate accepted surface"; enabled:!!panel.confirmed.reference; Layout.fillWidth:true; onClicked:workspace.inspectionPanel.navigate(panel.confirmed.reference.instance || panel.confirmed.reference.target,true) }
    UiButton { text:"Review fiber pin repairs"; visible:workspace.selectedData.kind==="FIBER"; Layout.fillWidth:true; onClicked:workspace.issuePanel.reviewPins(workspace.selectedId) }
    UiButton { text:"Hide placement evidence"; Layout.fillWidth:true; visible:!!panel.report.preview; onClicked:panel.tool.clear() }
    RouteInspection { visible:workspace.selectedData.engine==="ROUTED" }
}
