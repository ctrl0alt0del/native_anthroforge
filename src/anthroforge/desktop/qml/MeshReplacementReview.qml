import AnthroForge.Desktop 1.0
import QtQuick

ReplacementReview {
    id:dialog
    objectName:"meshReplacementReview"
    service:App.meshReplacement
    signal chooseFile()
    Connections { target:dialog.service; function onSelectionRequested() { dialog.chooseFile(); } }
}
