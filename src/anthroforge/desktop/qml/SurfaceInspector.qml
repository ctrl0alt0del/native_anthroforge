import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    readonly property var item: workspace.selectedData.kind === "SURFACE" ? authoring.state : ({})
    Layout.fillWidth: true; spacing: Theme.gap
    function setting(key,value) { const args={target:item.id}; args[key]=value; workspace.run("surface.update",args); }
    UiSection {
        title: "Curve surface"
        Label { text: panel.item.kind === "PATCH" ? "Closed boundary patch" : "Ordered curve loft"; color: Theme.muted }
        UiCheck { objectName: "surfaceExact"; text: "Preserve evaluated corners"; checked: panel.item.exact ?? true; onClicked: panel.setting("exact",checked) }
        UiCheck { objectName: "surfaceFlip"; text: "Flip normals"; checked: panel.item.flip || false; onClicked: panel.setting("flip",checked) }
        UiCheck { visible: panel.item.kind === "LOFT"; text: "Connect first and last rows"; checked: panel.item.close_across || false; onClicked: panel.setting("close_across",checked) }
        NumericSetting { visible: panel.item.kind === "LOFT"; label: "Across strips · 0 keeps fitted density"; value: panel.item.strips || 0; decimals: 0; onEdited: value => panel.setting("strips",Math.round(value)) }
        NumericSetting { visible: panel.item.kind === "PATCH"; label: "Patch resolution"; value: panel.item.patch_resolution || 4; decimals: 0; onEdited: value => panel.setting("patch_resolution",Math.round(value)) }
        UiButton { objectName: "surfaceRealign"; text: "Realign correspondence"; hint: "Recalculate direction, starting correspondence and fitted row density"; onClicked: workspace.run("surface.realign",{target:panel.item.id}) }
    }
    SurfaceSources { item: panel.item }
}
