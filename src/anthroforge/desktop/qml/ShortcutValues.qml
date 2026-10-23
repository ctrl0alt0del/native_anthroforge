import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

GridView {
    id: grid
    required property var values
    property string shortcutKey: ""
    required property var reference
    required property string numericType
    required property string dimension
    required property bool writable
    signal edited(int component, var value)
    Layout.fillWidth: true; Layout.preferredHeight: Math.min(160,Math.ceil(count/3)*35)
    cellWidth: width/Math.max(1,Math.min(3,count)); cellHeight: 35
    model: values; clip: true; ScrollBar.vertical: ScrollBar {}
    delegate: UiQuantityField {
        objectName: "shortcutValue"+grid.shortcutKey+":"+index
        required property int index
        required property var modelData
        width: grid.cellWidth-4; height: 30
        propertyReference: grid.reference.target ? Object.assign({},grid.reference,{component:grid.values.length>1 ? index : grid.reference.component}) : ({})
        canonicalValue: modelData; numericType: grid.numericType; dimension: grid.dimension
        enabled: grid.writable
        Accessible.name: grid.count===3 ? ["X","Y","Z"][index] : "Component "+(index+1)
        onCanonicalEdited: value => grid.edited(grid.values.length>1 ? index : -1,value)
    }
}
