import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiDialog {
    id:dialog
    objectName:"tissueSourcePicker"
    property var service:workspace.tissueRetarget
    title:"Choose tissue construction"; modal:true; anchors.centerIn:parent
    width:Math.min(560,parent.width-40); height:Math.min(500,parent.height-40)
    Connections { target:dialog.service; function onSelectionRequested() { search.text=""; dialog.open(); } }
    contentItem:ColumnLayout {
        spacing:Theme.gap
        UiField { id:search; Layout.fillWidth:true; placeholderText:"Search Anchors, Fibers and Membranes" }
        ListView {
            Layout.fillWidth:true; Layout.fillHeight:true; clip:true
            model:(dialog.service.choices || []).filter(c=>!search.text || (c.name+" "+c.kind).toLowerCase().includes(search.text.toLowerCase()))
            ScrollBar.vertical:ScrollBar {}
            delegate:UiButton {
                required property var modelData
                objectName:"tissueSource_"+modelData.id
                width:ListView.view.width-16
                text:modelData.name+" · "+modelData.kind+(modelData.current ? " · current" : "")
                alignLeft:true; enabled:!modelData.current
                onClicked: { dialog.close(); dialog.service.assess(modelData.id); }
            }
        }
        UiButton { Layout.alignment:Qt.AlignRight; text:"Cancel"; onClicked:dialog.close() }
    }
}
