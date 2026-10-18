import QtQuick

Item {
    required property var viewport
    readonly property var position: workspace.state.cursor || [0,0,0]
    readonly property point projected: { const camera=viewport.cameraState, distance=viewport.distance; return viewport.projectPoint(position[0],position[1],position[2]); }
    visible: viewport.pointInFront(position)
    x: projected.x-9; y: projected.y-9; width: 18; height: 18
    Rectangle { anchors.centerIn: parent; width: 12; height: 12; radius: 6; color: "transparent"; border.color: Theme.accent; border.width: 2 }
    Rectangle { anchors.centerIn: parent; width: 18; height: 1; color: Theme.text }
    Rectangle { anchors.centerIn: parent; width: 1; height: 18; color: Theme.text }
}
