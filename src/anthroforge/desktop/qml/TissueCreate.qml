import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Layouts

ColumnLayout {
    id: panel
    required property var selected
    Layout.fillWidth: true; spacing: Theme.gap
    UiCombo {
        id: preset; objectName: "tissueCreationPreset"; Layout.fillWidth: true
        model: panel.selected.tissue_presets || []; textRole: "name"; valueRole: "id"
        hint: "Editable creation defaults; the classification does not restrict algorithms"
    }
    UiButton {
        objectName: "createTissue"; text: "Create tissue"; Layout.fillWidth: true
        enabled: !!preset.currentValue
        onClicked: App.construction.createConstruction("tissue.create",{source:panel.selected.id,preset:preset.currentValue})
    }
}
