import QtQuick
import QtQuick.Controls

Item {
    id: root
    required property var viewport
    ViewSnapshot { id: evidence; source: workspace.surfaceMeasurements }
    Repeater {
        model:evidence.data.lines?.length ? 5 : 0
        Label {
            required property int index
            readonly property var values:index<3 ? evidence.data.lines : evidence.data.section?.lines || []
            readonly property var end:values[2*(index<3 ? index : index-3)+1]
            readonly property point screen:end ? root.viewport.projectPoint(end[0],end[1],end[2]) : Qt.point(-100,-100)
            visible:!!end && root.viewport.pointInFront(end)
            x:screen.x+4; y:screen.y-16
            text:["X","Y","Z","U","V"][index]
            color:["#ed7474","#79d08c","#75a7ef","#f5ca70","#77dfd6"][index]
            font.bold:true
            background:Rectangle { color:Theme.panel; opacity:.8 }
        }
    }
}
