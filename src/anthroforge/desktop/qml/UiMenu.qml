import QtQuick
import QtQuick.Controls

Menu {
    objectName: "menu" + title
    implicitWidth: 264
    padding: 4
    margins: Theme.gap
    delegate: UiMenuItem {}
    background: Rectangle { color: Theme.panel; border.color: Theme.border; radius: Theme.radius + 2 }
}
