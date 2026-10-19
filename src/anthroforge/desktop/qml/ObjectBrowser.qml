import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: browser
    required property var keyboard
    signal importRequested()
    signal deleteRequested(string entity)
    property int currentIndex: 0
    readonly property string selected: workspace.selectedId
    spacing: Theme.gap
    onSelectedChanged: Qt.callLater(revealSelection)
    function revealSelection() {
        if(selected) currentIndex=workspace.selectedData.is_construction || workspace.selectedData.is_control ? 1 : 0;
    }
    RowLayout {
        Layout.fillWidth: true; spacing: Theme.gap
        UiButton { objectName: "anatomyTab"; text: "Anatomy"; hint: "SCP / VCP hierarchy"; Layout.fillWidth: true; checked: browser.currentIndex===0; onClicked: browser.currentIndex=0 }
        UiButton { objectName: "constructionTab"; text: "Construction"; hint: "Curves, fibers, surfaces and reference images"; Layout.fillWidth: true; checked: browser.currentIndex===1; onClicked: browser.currentIndex=1 }
    }
    StackLayout {
        Layout.fillWidth: true; Layout.fillHeight: true
        currentIndex: browser.currentIndex
        Outliner { onImportRequested: browser.importRequested(); onDeleteRequested: entity => browser.deleteRequested(entity) }
        Construction { keyboard: browser.keyboard }
    }
}
