import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiDialog {
    id: dialog
    objectName: "tissueCreationDialog"
    parent: Overlay.overlay
    title: "Create Tissue"; modal: true; width: 460
    property string source: ""
    readonly property var sources: { const revision=workspace.state.revision; return workspace.tissueSources(); }
    readonly property var selected: sources.find(r=>r.id===source) || ({})
    function request() {
        const current=sources.find(r=>r.id===workspace.selectedId);
        if(current) { workspace.createConstruction("tissue.create",{source:current.id}); return; }
        source=""; search.text=""; open();
    }
    ColumnLayout {
        width: parent.width; spacing: Theme.gap
        Label { text:"Choose an Anchor, Fiber or Membrane as the tissue source."; color:Theme.text; Layout.fillWidth:true; wrapMode:Text.WordWrap }
        UiField { id:search; placeholderText:"Find construction source…"; Layout.fillWidth:true }
        ListView {
            id:list; objectName:"tissueSourceList"; Layout.fillWidth:true; Layout.preferredHeight:220
            clip:true; reuseItems:true; model:dialog.sources.filter(r=>r.name.toLowerCase().includes(search.text.toLowerCase()))
            ScrollBar.vertical:ScrollBar {}
            delegate:UiButton {
                required property var modelData
                width:list.width; height:36; text:modelData.name; alignLeft:true
                flatStyle:true; checkable:true; checked:dialog.source===modelData.id
                onClicked:dialog.source=modelData.id
            }
        }
        Label { visible:!dialog.sources.length; text:"No attached construction yet. Create a Fiber from a curve, an Anchor from a point, or a Membrane from Fibers. These source objects remain editable."; color:Theme.muted; Layout.fillWidth:true; wrapMode:Text.WordWrap }
        UiCombo { id:preset; Layout.fillWidth:true; model:dialog.selected.presets || []; textRole:"name"; valueRole:"id" }
        RowLayout {
            Layout.alignment:Qt.AlignRight
            UiButton { text:"Cancel"; onClicked:dialog.close() }
            UiButton { objectName:"createChosenTissue"; text:"Create Tissue"; primary:true; enabled:!!dialog.selected.id && !!preset.currentValue; onClicked:{ workspace.createConstruction("tissue.create",{source:dialog.source,preset:preset.currentValue}); dialog.close(); } }
        }
    }
}
