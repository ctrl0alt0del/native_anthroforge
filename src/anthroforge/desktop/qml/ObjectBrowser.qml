import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: browser
    required property var keyboard
    signal importRequested()
    signal deleteRequested(string entity)
    property alias currentIndex: tabs.currentIndex
    readonly property string selected: App.selection.selectedId
    spacing: Theme.gap
    onSelectedChanged: Qt.callLater(revealSelection)
    function revealSelection() {
        if(selected) tabs.setCurrentIndex(App.selection.selectedData.is_construction || App.selection.selectedData.is_control ? 1 : 0);
    }
    UiTabBar {
        id: tabs
        objectName: "objectTabs"
        Layout.fillWidth: true
        UiTabButton { objectName: "anatomyTab"; text: "Anatomy"; hint: "SCP / VCP hierarchy" }
        UiTabButton { objectName: "constructionTab"; text: "Construction"; hint: "Curves, fibers, surfaces and reference images" }
    }
    StackLayout {
        Layout.fillWidth: true; Layout.fillHeight: true
        currentIndex: browser.currentIndex
        Outliner { onImportRequested: browser.importRequested(); onDeleteRequested: entity => browser.deleteRequested(entity) }
        Construction { keyboard: browser.keyboard }
    }
}
