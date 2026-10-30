import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiSection {
    id: section
    required property var reports
    readonly property var finalReport: reports.final?.report || ({})
    readonly property var solver: finalReport.solver || ({})
    readonly property var contact: finalReport.contact || ({})
    readonly property var clearance: finalReport.anatomy_clearance || ({})
    readonly property var budgets: reports.topology?.report?.budgets || []
    title: "Skin diagnostics"; expanded: false; stateKey: "skin-diagnostics"
    visible: !!reports.final?.geometry || !!reports.topology?.geometry
    hint: "Checks describe the saved result. They do not repair skin. Full findings are in Issues."
    UiButton { objectName:"checkSkinGeometry"; text:"Locate geometry findings"; Layout.fillWidth:true; hint:"Run an on-demand spatial check of the accepted skin surface."; onClicked:App.spatialEvidence.check("skin",section.reports.final?.geometry ? "final" : "topology") }
    SurfaceMeasurements { target:"skin"; stage:section.reports.final?.geometry ? "final" : "topology" }
    UiButton { text:"Section skin"; Layout.fillWidth:true; onClicked:App.sectionTools.inspect("skin",section.reports.final?.geometry ? "final" : "topology") }
    TissueSections { visible:App.sectionTools.state.enabled && App.sectionTools.state.target.startsWith("skin:") }
    UiDetail { label:"Revision"; value:String(section.reports.final?.revision ?? "—") }
    UiDetail { label:"Solve steps"; value:String(section.solver.iterations ?? "—") }
    UiDetail { label:"Minimum J"; value:section.solver.minimum_proxy_j === undefined ? "—" : Number(section.solver.minimum_proxy_j).toPrecision(4) }
    UiDetail { label:"Outside proxy"; value:String(section.solver.outside_embeddings ?? "—") }
    UiDetail { label:"Crossings"; value:String(section.finalReport.intersections?.self_intersections ?? "Unknown") }
    UiDetail { label:"New witnesses"; value:section.finalReport.crossing_comparison ? String(section.finalReport.crossing_comparison.new_witnesses)+(section.finalReport.crossing_comparison.complete ? "" : " · partial comparison") : "—" }
    UiDetail { label:"Motion violations"; value:section.contact.published_motion_violations === undefined || section.contact.published_motion_violations < 0 ? "Unknown" : String(section.contact.published_motion_violations) }
    UiDetail { label:"Clearance samples"; value:String(section.clearance.samples ?? "Unknown") }
    UiDetail { label:"Negative samples"; value:section.clearance.negative_samples === undefined ? "Unknown" : String(section.clearance.negative_samples)+" · reference "+String(section.clearance.reference_negative_samples) }
    UiHelp { explanation:"Sampled clearance uses nearest-point normals. It does not establish whether the anatomy penetrates the skin volume." }
    Label { text:"Topology budgets · actual / requested"; visible:section.budgets.length>0; color:Theme.muted; wrapMode:Text.Wrap; Layout.fillWidth:true }
    UiField { id: search; visible:section.budgets.length>0; placeholderText:"Search budget regions"; Layout.fillWidth:true }
    ListView {
        objectName:"skinAchievedBudgets"; visible:section.budgets.length>0
        Layout.fillWidth:true; Layout.preferredHeight:144; clip:true
        model:section.budgets.filter(row => (row.label || row.owner || "Root remainder").toLowerCase().includes(search.text.toLowerCase()))
        ScrollBar.vertical: ScrollBar {}
        delegate: ColumnLayout {
            required property var modelData
            width:ListView.view.width; spacing:2
            Label { text:modelData.label || modelData.owner || "Root remainder"; wrapMode:Text.Wrap; color:Theme.text; Layout.fillWidth:true }
            Label { text:String(modelData.actual_exclusive_quads ?? "Unknown")+" / "+String(modelData.exclusive)+" quads"; color:Theme.muted }
        }
    }
}
