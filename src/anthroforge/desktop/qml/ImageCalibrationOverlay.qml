import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: overlay
    required property var viewport
    anchors.fill: parent
    readonly property var state: App.imageTools.state
    visible: state.active
    Repeater {
        model: overlay.state.points
        Rectangle {
            required property var modelData
            readonly property point screen: { const camera=overlay.viewport.cameraState, distance=overlay.viewport.distance; return overlay.viewport.projectPoint(...modelData.position); }
            x: screen.x-5; y: screen.y-5; width: 10; height: 10; radius: 5
            color: Theme.accent; border.color: Theme.text
        }
    }
    Rectangle {
        anchors.horizontalCenter: parent.horizontalCenter; anchors.bottom: parent.bottom; anchors.bottomMargin: 60
        width: Math.min(380,parent.width-24); height: controls.implicitHeight+24
        color: Theme.panel; border.color: Theme.border; radius: 5
        ColumnLayout {
            id: controls; anchors.fill: parent; anchors.margins: 12
            Label { text: overlay.state.points.length < 2 ? "Pick "+(overlay.state.points.length ? "second" : "first")+" image landmark" : "Distance between landmarks"; color: Theme.text }
            NumericSetting { live: false; visible: overlay.state.points.length === 2; label: "Distance"; length: true; value: overlay.distance; onEdited: value => overlay.distance=value }
            RowLayout {
                UiButton { text: "Calibrate"; primary: true; enabled: overlay.state.points.length===2 && overlay.distance>0; onClicked: App.imageTools.accept(overlay.distance) }
                UiButton { text: "Cancel"; onClicked: App.imageTools.cancel() }
            }
        }
    }
    property real distance: 1
}
