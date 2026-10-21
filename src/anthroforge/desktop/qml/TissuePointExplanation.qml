import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiSection {
    id: panel
    required property var report
    title: "Point explanation"; expanded: !!report.asset
    function vector(values) { return (values || []).map(v=>Number(v).toPrecision(5)).join(", "); }
    Label { Layout.fillWidth: true; text: panel.report.asset ? panel.report.stage+" · part "+panel.report.point.part+" · material face "+panel.report.point.material_face : "Choose Explain, then click the tissue surface."; color: Theme.muted; wrapMode: Text.WordWrap }
    Label { visible: !!panel.report.asset; Layout.fillWidth: true; text: "Local XYZ · m: "+panel.vector(panel.report.point?.position)+"\nFrom base · m: "+panel.vector(panel.report.point?.displacement)+"\nSurface normal: "+panel.vector(panel.report.point?.normal); color: Theme.text; wrapMode: Text.WrapAnywhere }
    Label { visible: !!panel.report.asset; Layout.fillWidth: true; text: "Yellow: inspected face, point, base displacement and surface normal. Constraints explain inputs; they are not a solver-force decomposition."; color: Theme.muted; wrapMode: Text.WordWrap }
    Repeater {
        model: panel.report.annotations || []
        Label { required property string modelData; Layout.fillWidth: true; text: modelData; color: Theme.text; wrapMode: Text.WordWrap }
    }
    Repeater {
        model: panel.report.constraints || []
        Label { required property var modelData; Layout.fillWidth: true; text: modelData.mask+" · "+modelData.mode+" · influence "+modelData.influence.toFixed(3)+(modelData.fixed_fraction>0 ? " · exact core" : "")+(modelData.target ? " · target-relative" : " · source-relative")+(modelData.goal ? "\nGoal XYZ · m: "+panel.vector(modelData.goal)+"\nResult → goal · m: "+modelData.residual.toPrecision(5) : ""); color: Theme.text; wrapMode: Text.WrapAnywhere }
    }
    Label { visible: !!panel.report.asset && !(panel.report.constraints || []).length; Layout.fillWidth: true; text: "No authored region constraint influences this point in the inspected stage."; color: Theme.muted; wrapMode: Text.WordWrap }
    Label { visible: !!panel.report.goal_note; Layout.fillWidth: true; text: panel.report.goal_note || ""; color: Theme.muted; wrapMode: Text.WordWrap }
    UiNotice { text: panel.report.goal_error || ""; error: true }
    UiSection {
        title: "Current construction sources"; expanded: false
        Repeater {
            model: panel.report.sources || []
            UiButton { required property var modelData; text: modelData.name; Layout.fillWidth: true; hint: "Anatomical supports: "+(modelData.supports || []).map(s=>s.name+" ("+s.role+")").join(", "); onClicked: workspace.select(modelData.id) }
        }
    }
}
