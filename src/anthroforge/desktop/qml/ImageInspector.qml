import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

ColumnLayout {
    id: panel
    readonly property var selected: workspace.selectedData
    readonly property var style: selected.image_style || {}
    readonly property bool dialogVisible: replaceFile.visible
    Layout.fillWidth: true; spacing: Theme.gap
    function appearance(key,value) {
        const options={target:selected.id}; options[key]=value;
        workspace.run("image.presentation",options);
    }
    UiSection {
        title: "Reference image"
        NumericSetting { label: "Width"; length: true; value: panel.selected.dimensions?.[0] || 1; onEdited: value => workspace.run("image.size",{target:panel.selected.id,width:value}) }
        Label { text: "Height: "+((panel.selected.dimensions?.[1] || 1)/workspace.state.unit_factor).toFixed(4)+" "+workspace.state.display_units; color: Theme.muted }
        RowLayout {
            UiButton { text: "Replace…"; hint: "Replace this assignment, keeping its width and position"; onClicked: replaceFile.open() }
            UiButton { text: "Instance"; hint: "Independent placement using the same image asset"; onClicked: { const id=workspace.run("image.instance",{source:panel.selected.id}); if(id) workspace.select(id); } }
        }
        UiButton { objectName: "calibrateImage"; text: "Calibrate distance…"; Layout.fillWidth: true; enabled: !workspace.state.editing; onClicked: workspace.imageTools.start() }
        RowLayout {
            Label { text: "Face axis"; color: Theme.muted; Layout.fillWidth: true }
            Repeater { model: ["X","Y","Z"]; UiButton { required property string modelData; text: modelData; onClicked: workspace.run("image.align",{target:panel.selected.id,axis:modelData}) } }
        }
    }
    UiSection {
        title: "Appearance"; hint: "Appearance belongs to this workspace and does not change authored image placement."
        NumericSetting { label: "Opacity"; decimals: 2; value: panel.style.opacity ?? .65; onEdited: value => panel.appearance("opacity",value) }
        UiCombo { Layout.fillWidth: true; model: ["Normal depth","In front","Behind geometry"]; currentIndex: Math.max(0,["NORMAL","FRONT","BACK"].indexOf(panel.style.depth)); onActivated: panel.appearance("depth",["NORMAL","FRONT","BACK"][currentIndex]) }
        UiCombo { Layout.fillWidth: true; model: ["Both sides","Front side","Back side"]; currentIndex: Math.max(0,["BOTH","FRONT","BACK"].indexOf(panel.style.side)); onActivated: panel.appearance("side",["BOTH","FRONT","BACK"][currentIndex]) }
        UiCheck { text: "Orthographic views"; checked: panel.style.orthographic ?? true; onClicked: panel.appearance("orthographic",checked) }
        UiCheck { text: "Perspective views"; checked: panel.style.perspective ?? true; onClicked: panel.appearance("perspective",checked) }
        UiCheck { objectName: "imageAxisVisibility"; text: "Only axis-aligned views"; checked: panel.style.only_axis_aligned ?? false; onClicked: panel.appearance("only_axis_aligned",checked) }
        UiCheck { text: "Pick in viewport"; checked: panel.style.pickable ?? true; onClicked: panel.appearance("pickable",checked) }
    }
    FileDialog { id: replaceFile; title: "Replace reference image"; nameFilters: ["Reference images (*.png *.jpg *.jpeg)"]; onAccepted: workspace.imageTools.importFile(selectedFile.toString(),true) }
}
