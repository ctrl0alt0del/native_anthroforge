import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

GridView {
    id: grid
    required property var values
    required property var reference
    required property string numericType
    required property string dimension
    required property bool writable
    readonly property real factor: dimension === "LENGTH" ? workspace.state.unit_factor : dimension === "ANGLE" ? Math.PI/180 : 1
    signal edited(int component, real value)
    Layout.fillWidth: true; Layout.preferredHeight: Math.min(160,Math.ceil(count/3)*35)
    cellWidth: width/Math.max(1,Math.min(3,count)); cellHeight: 35
    model: values; clip: true; ScrollBar.vertical: ScrollBar {}
    delegate: UiNumberField {
        required property int index
        required property real modelData
        width: grid.cellWidth-4; height: 30
        propertyReference: grid.reference.target ? Object.assign({},grid.reference,{component:grid.values.length>1 ? index : grid.reference.component}) : ({})
        value: modelData/grid.factor; decimals: grid.numericType === "INTEGER" ? 0 : 4
        enabled: grid.writable
        Accessible.name: grid.count===3 ? ["X","Y","Z"][index] : "Component "+(index+1)
        onEdited: value => grid.edited(grid.values.length>1 ? index : -1,value*grid.factor)
    }
}
