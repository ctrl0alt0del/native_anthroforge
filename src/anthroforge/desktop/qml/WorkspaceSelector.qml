import QtQuick

UiCombo {
    objectName: "workspaceSelector"
    model: workspace.state.workspaces
    currentIndex: workspace.state.workspace
    // Model replacement can reset ComboBox's index after bindings have evaluated.
    onModelChanged: Qt.callLater(synchronize)
    function synchronize() { currentIndex=Qt.binding(()=>workspace.state.workspace); }
    onActivated: { workspace.run("workspace.select",{index:currentIndex}); synchronize(); }
}
