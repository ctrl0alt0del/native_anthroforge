import QtQuick

ReplacementReview {
    id:dialog
    objectName:"meshReplacementReview"
    service:workspace.meshReplacement
    signal chooseFile()
    Connections { target:dialog.service; function onSelectionRequested() { dialog.chooseFile(); } }
}
