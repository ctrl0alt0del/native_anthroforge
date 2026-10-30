import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Dialogs

FileDialog {
    id: picker
    objectName: "referenceImageDialog"
    title: "Import reference image"
    nameFilters: ["Reference images (*.png *.jpg *.jpeg)"]
    function request(parentId,axis) {
        if(App.imageTools.prepareImport(parentId,axis)) open();
    }
    onAccepted: App.imageTools.acceptImport(selectedFile.toString())
    onRejected: App.imageTools.cancelImport()
}
