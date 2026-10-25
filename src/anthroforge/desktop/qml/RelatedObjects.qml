import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    property var rows: []
    readonly property var shown: rows.filter(row=>caption(row).toLowerCase().includes(search.text.toLowerCase()))
    Layout.fillWidth:true; spacing:4
    function caption(row) { return row.name+" · "+(row.output || row.reason || ""); }
    UiField { id:search; objectName:panel.objectName+"Search"; visible:panel.rows.length>8; Layout.fillWidth:true; placeholderText:"Search related objects" }
    ListView {
        objectName:panel.objectName+"List"; Layout.fillWidth:true; Layout.preferredHeight:Math.min(8,panel.rows.length)*34
        model:panel.shown; clip:true; reuseItems:true; cacheBuffer:0; spacing:4
        ScrollBar.vertical:ScrollBar {}
        delegate:RelatedObject { required property var modelData; width:ListView.view.width; height:30; targetId:modelData.owner || modelData.id; label:panel.caption(modelData) }
        Label { anchors.centerIn:parent; visible:panel.rows.length>0 && !panel.shown.length; text:"No matching objects"; color:Theme.muted }
    }
}
