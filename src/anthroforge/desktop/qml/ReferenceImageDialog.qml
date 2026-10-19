import QtQuick
import QtQuick.Dialogs

FileDialog {
    id: picker
    objectName: "referenceImageDialog"
    title: "Import reference image"
    nameFilters: ["Reference images (*.png *.jpg *.jpeg)"]
    function request(parentId,axis) {
        if(workspace.imageTools.prepareImport(parentId,axis)) open();
    }
    onAccepted: workspace.imageTools.acceptImport(selectedFile.toString())
    onRejected: workspace.imageTools.cancelImport()
}
