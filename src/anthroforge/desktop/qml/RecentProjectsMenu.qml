import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQml.Models

UiMenu {
    id: menu
    title: "Recent Projects"
    objectName: "recentProjectsMenu"
    Instantiator {
        model: App.projectLibrary.recentProjects
        delegate: UiMenuItem {
            required property var modelData
            text: modelData.name
            detail: modelData.directory
            hint: modelData.path
            onTriggered: App.projectLibrary.openRecent(modelData.path)
        }
        onObjectAdded: (index, object) => menu.insertItem(index, object)
        onObjectRemoved: (index, object) => menu.removeItem(object)
    }
    UiMenuItem { text: "No recent projects"; enabled: false; visible: !App.projectLibrary.recentProjects.length }
    MenuSeparator { visible: !!App.projectLibrary.recentProjects.length }
    UiMenuItem {
        objectName: "clearRecentProjects"
        text: "Clear recent projects"
        enabled: !!App.projectLibrary.recentProjects.length || !!App.projectLibrary.error
        onTriggered: App.projectLibrary.clearRecent()
    }
}
