import QtQuick
import QtQuick.Controls
import QtQml.Models

UiMenu {
    id: menu
    title: "Recent Projects"
    objectName: "recentProjectsMenu"
    Instantiator {
        model: workspace.projectLibrary.recentProjects
        delegate: UiMenuItem {
            required property var modelData
            text: modelData.name
            detail: modelData.directory
            hint: modelData.path
            onTriggered: workspace.projectLibrary.openRecent(modelData.path)
        }
        onObjectAdded: (index, object) => menu.insertItem(index, object)
        onObjectRemoved: (index, object) => menu.removeItem(object)
    }
    UiMenuItem { text: "No recent projects"; enabled: false; visible: !workspace.projectLibrary.recentProjects.length }
    MenuSeparator { visible: !!workspace.projectLibrary.recentProjects.length }
    UiMenuItem {
        objectName: "clearRecentProjects"
        text: "Clear recent projects"
        enabled: !!workspace.projectLibrary.recentProjects.length || !!workspace.projectLibrary.error
        onTriggered: workspace.projectLibrary.clearRecent()
    }
}
