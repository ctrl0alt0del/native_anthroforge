import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: pane
    readonly property var service: workspace.reconstructionPanel
    spacing: Theme.gap
    RowLayout {
        Layout.fillWidth: true
        Label { text: "Reconstruction"; color: Theme.text; font.bold: true; Layout.fillWidth: true }
        UiButton { text: service.floating ? "Dock" : "Detach"; onClicked: service.setFloating(!service.floating) }
        UiButton { text: "×"; hint: "Close panel"; onClicked: service.setOpen(false) }
    }
    UiCombo { Layout.fillWidth: true; model: ["Variants","Catalogue","Regions","Stages","Reviews","Queue"]; currentIndex: model.indexOf(pane.service.page); onActivated: pane.service.setPage(currentText) }
    ScrollView {
        id: scroll; Layout.fillWidth: true; Layout.fillHeight: true; clip: true
        contentWidth: availableWidth; contentHeight: pageLoader.implicitHeight
        Loader {
            id: pageLoader; width: scroll.availableWidth
            source: ({Variants:"ReconstructionVariants.qml",Catalogue:"ReconstructionCatalogue.qml",Regions:"ReconstructionRegions.qml",Stages:"ReconstructionStages.qml",Reviews:"ReconstructionReviews.qml",Queue:"ReconstructionQueue.qml"})[pane.service.page] || ""
        }
    }
}
