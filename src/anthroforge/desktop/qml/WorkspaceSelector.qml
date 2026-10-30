import AnthroForge.Desktop 1.0
import QtQuick

UiCombo {
    objectName: "workspaceSelector"
    model: App.runtime.state.workspaces
    currentIndex: App.runtime.state.workspace
    // Model replacement can reset ComboBox's index after bindings have evaluated.
    onModelChanged: Qt.callLater(synchronize)
    function synchronize() { currentIndex=Qt.binding(()=>App.runtime.state.workspace); }
    onActivated: { App.runtime.run("App.selection.select",{index:currentIndex}); synchronize(); }
}
