import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiSection {
    id: panel
    required property string target
    required property string stage
    readonly property var tool: App.surfaceMeasurements.volume
    readonly property var report: tool.state.report || ({})
    title:"Inside another surface"; expanded:false
    SurfaceSelector { id:volumeTarget }
    UiButton { text:"Check sampled containment"; Layout.fillWidth:true; enabled:!!volumeTarget.current.id && volumeTarget.current.ready; onClicked:panel.tool.compare(panel.target,panel.stage,volumeTarget.current.instance || volumeTarget.current.id,volumeTarget.current.role) }
    UiDetail { label:"Sampled surface"; value:panel.report.surface?.name || "—" }
    UiDetail { label:"Enclosing surface"; value:panel.report.volume?.name || "—" }
    UiDetail { label:"Inside / boundary / outside"; value:panel.report.available ? [panel.report.inside,panel.report.boundary,panel.report.outside].join(" / ") : "—" }
    UiDetail { label:"Deepest inside sample"; value:panel.report.available ? (panel.report.maximum_inside_distance/App.runtime.state.unit_factor).toPrecision(5)+" "+App.runtime.state.display_units : "—" }
    UiDetail { label:"Samples / vertices"; value:panel.report.available ? panel.report.sampled+" / "+panel.report.vertices : "—" }
    UiNotice { text:panel.report.reason || panel.tool.state.error || (panel.tool.state.state==="stale" ? "Geometry changed. Run the check again." : "") }
    UiHelp { explanation:"Checks up to 512 source vertices against a closed, consistently oriented exterior volume. The yellow segment marks the deepest sampled point. Samples do not prove whole-surface containment or measure the translation needed to separate objects." }
    UiButton { text:"Hide volume witness"; visible:!!panel.report.surface; Layout.fillWidth:true; onClicked:panel.tool.clear() }
}
