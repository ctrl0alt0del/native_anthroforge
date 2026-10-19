import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiSection {
    id: panel
    required property var settings
    property var diagnostic
    signal edited(string key,var value)
    title: "Height smoothing"; expanded: false
    UiCombo { objectName: "tissueSmoothingMode"; Layout.fillWidth: true; model: ["OFF","HEIGHT"]; currentIndex: model.indexOf(panel.settings.mode); onActivated: panel.edited("mode",currentText) }
    NumericSetting { label: "Radius"; length: true; value: panel.settings.radius ?? 0.2; onEdited: value=>panel.edited("radius",value) }
    NumericSetting { label: "Strength"; value: panel.settings.strength ?? 0.8; onEdited: value=>panel.edited("strength",value) }
    NumericSetting { label: "Maximum change"; length: true; value: panel.settings.maximum_change ?? 0.05; onEdited: value=>panel.edited("maximum_change",value) }
    Label { visible: !!panel.diagnostic; Layout.fillWidth: true; wrapMode: Text.WordWrap; color: Theme.muted; text: panel.diagnostic ? panel.diagnostic.status+" · "+panel.diagnostic.pinned+" fixed samples" : "" }
}
