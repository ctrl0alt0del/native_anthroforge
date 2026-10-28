import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiSection {
    id: panel
    title: "Cross-section"; expanded: false
    readonly property var tool: workspace.sectionTools
    UiCheck { objectName: "sectionEnabled"; text: "Show section"; checked: panel.tool.state.enabled; onToggled: panel.tool.enable(checked) }
    ColumnLayout {
        visible: panel.tool.state.enabled; Layout.fillWidth: true
        UiCombo { objectName: "sectionAxis"; Layout.fillWidth: true; model: ["X plane","Y plane","Z plane"]; currentIndex: panel.tool.state.axis; onActivated: panel.tool.setting("axis",currentIndex) }
        NumericSetting { objectName: "sectionPosition"; label: "Plane position · m"; value: panel.tool.state.position; onEdited: value=>panel.tool.setting("position",value) }
        UiButton { text: "Center on surface"; Layout.fillWidth: true; onClicked: panel.tool.center() }
        UiCheck { text: "Cut away one side"; checked: panel.tool.state.cut; onToggled: panel.tool.setting("cut",checked) }
        UiCheck { text: "Flip visible side"; checked: panel.tool.state.flip; onToggled: panel.tool.setting("flip",checked) }
        UiCheck { text: "Cut surrounding geometry"; checked: panel.tool.state.wholeScene; onToggled: panel.tool.setting("whole_scene",checked) }
        Label { text: "The same world plane crosses the displayed stages. Pink: selected stage; green: reference. Sectioning never changes anatomy."; color: Theme.muted; wrapMode: Text.WordWrap; Layout.fillWidth: true }
    }
    UiNotice { text: panel.tool.state.error; error: true }
}
