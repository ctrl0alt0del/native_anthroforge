import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiSection {
    id: panel
    title: "Size & section"; expanded: false; stateKey: "inspect/size"
    property string target: workspace.selectedId
    property string stage: workspace.selectedData.is_tissue ? (workspace.tissueInspection.state.stage || "final") : "final"
    readonly property var tool: workspace.surfaceMeasurements
    readonly property bool active: tool.state.enabled && tool.state.target===target
    readonly property var report: active ? tool.state.report : ({})
    function length(value) { return typeof value==="number" ? (value/workspace.state.unit_factor).toPrecision(5)+" "+workspace.state.display_units : "—"; }
    UiCheck { text:"Show dimensions and axes"; checked:panel.active; onToggled:checked ? panel.tool.show(panel.target,panel.stage) : panel.tool.cancel() }
    onStageChanged: if(active) tool.show(target,stage)
    UiDetail { label:"World X"; value:panel.length(panel.report.extents?.[0]) }
    UiDetail { label:"World Y"; value:panel.length(panel.report.extents?.[1]) }
    UiDetail { label:"World Z"; value:panel.length(panel.report.extents?.[2]) }
    UiDetail { label:"Section U"; value:panel.length(panel.report.section?.available ? panel.report.section.spans[0] : undefined) }
    UiDetail { label:"Section V"; value:panel.length(panel.report.section?.available ? panel.report.section.spans[1] : undefined) }
    UiDetail { label:"Revision"; value:panel.report.surface ? String(panel.report.surface.revision)+" · "+panel.report.surface.stage : "—" }
    UiHelp { explanation:"Overall dimensions use world axes. Section U/V follow the axes shown on the cutting plane; they are spans, not enclosed area." }
    UiNotice { text:panel.report.section?.truncated ? "Section limit reached: spans cover the retained contour only." : "" }
    UiNotice { text:panel.tool.state.error; error:true }
    UiSection {
        title:"Scale & topology"; expanded:false
        readonly property var data: panel.report.conditioning || ({})
        UiDetail { label:"Shortest edge"; value:panel.length(panel.report.conditioning?.minimum_edge) }
        UiDetail { label:"Longest edge"; value:panel.length(panel.report.conditioning?.maximum_edge) }
        UiDetail { label:"Open edges"; value:String(panel.report.conditioning?.boundary_edges ?? "—") }
        UiDetail { label:"Nonmanifold"; value:String(panel.report.conditioning?.nonmanifold_edges ?? "—") }
        UiDetail { label:"Winding conflicts"; value:String(panel.report.conditioning?.orientation_conflicts ?? "—") }
        UiDetail { label:"Thin triangles"; value:panel.report.conditioning ? Number(panel.report.conditioning.minimum_triangle_quality).toPrecision(4) : "—" }
        UiDetail { label:"Transform condition"; value:panel.report.conditioning ? Number(panel.report.conditioning.transform_condition).toPrecision(4) : "—" }
        UiHelp { explanation:"Triangle quality is twice area divided by longest edge squared. Near zero means thin or collapsed triangles. A large transform condition means uneven scaling. These are measurements, not automatic repairs." }
    }
    VolumeInspection { target:panel.target; stage:panel.stage }
}
