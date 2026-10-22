import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiSection {
    id: panel
    required property var item
    property var masks: []
    property string focused: ""
    readonly property var selected: item.constraints?.find(r=>r.id===focused)
    title: "Constraints"; expanded: false
    hint: "Fixed cores are exact; feathered surroundings are soft. Structural shell backing remains exact."
    function change(key,value) { const changes={}; changes[key]=value; workspace.run("tissue.constraint.update",{target:item.id,constraint:focused,changes:changes}); }
    RowLayout {
        Layout.fillWidth: true
        UiCombo { id: mask; objectName: "tissueRegionMask"; Layout.fillWidth: true; model: panel.masks }
        UiButton { objectName: "tissueRegionAdd"; text: "Add"; enabled: !!mask.currentText; onClicked: panel.focused=workspace.run("tissue.constraint.add",{target:panel.item.id,mask:mask.currentText}) || "" }
    }
    UiField { id: search; objectName: "tissueRegionSearch"; Layout.fillWidth: true; placeholderText: "Find a region…"; visible: (panel.item.constraints?.length || 0)>0 }
    ListView {
        id: regions; objectName: "tissueRegionList"; Layout.fillWidth: true
        Layout.preferredHeight: Math.min(160,count*32); clip: true; reuseItems: true
        model: (panel.item.constraints || []).filter(r=>(r.mask+" "+r.mode).toLowerCase().includes(search.text.toLowerCase()))
        ScrollBar.vertical: ScrollBar {}
        delegate: UiButton {
            required property var modelData
            width: regions.width; height: 32; flatStyle: true; alignLeft: true
            text: modelData.mask + " · " + modelData.mode; checkable: true; checked: panel.focused===modelData.id
            onClicked: panel.focused=modelData.id
        }
    }
    ColumnLayout {
        visible: !!panel.selected; Layout.fillWidth: true; spacing: Theme.gap
        UiCombo { objectName: "tissueRegionMode"; Layout.fillWidth: true; model: ["FIXED","SOFT"]; currentIndex: model.indexOf(panel.selected?.mode); onActivated: panel.change("mode",currentText) }
        NumericSetting { propertyReference: ({target:panel.item.id,path:["constraints","@"+(panel.selected?.id || ""),"strength"]}); label: "Soft strength"; value: panel.selected?.strength || 0; onEdited: value=>panel.change("strength",value) }
        NumericSetting { propertyReference: ({target:panel.item.id,path:["constraints","@"+(panel.selected?.id || ""),"feather"]}); label: "Feather"; value: panel.selected?.feather || 0; onEdited: value=>panel.change("feather",value) }
        NumericSetting { propertyReference: ({target:panel.item.id,path:["constraints","@"+(panel.selected?.id || ""),"offset"]}); label: "Normal offset"; length: true; value: panel.selected?.offset || 0; onEdited: value=>panel.change("offset",value) }
        UiSection {
            title: "Goal target"; expanded: !!panel.selected?.reference
            hint: "Bind the inflated rest positions to a target. Offsets then follow its surface normals."
            Label { text: panel.selected?.reference ? "Attached goals" : "Goals follow source"; color: Theme.muted }
            SurfaceSelector { id: goal; objectName: "tissueRegionTarget"; target: panel.selected?.reference?.target || ""; role: panel.selected?.reference?.role || "" }
            RowLayout {
                Layout.fillWidth: true
                UiButton { objectName: "tissueRegionBind"; text: panel.selected?.reference ? "Rebind" : "Bind target"; enabled: !!goal.current.ready; Layout.fillWidth: true; onClicked: workspace.run("tissue.constraint.bind",{target:panel.item.id,constraint:panel.focused,parent:goal.current.id,role:goal.current.role}) }
                UiButton { objectName: "tissueRegionUnlink"; text: "Use source"; enabled: !!panel.selected?.reference; onClicked: workspace.run("tissue.constraint.unlink",{target:panel.item.id,constraint:panel.focused}) }
            }
        }
        UiButton { objectName: "tissueRegionRemove"; text: "Remove region"; glyph: "delete"; Layout.fillWidth: true; onClicked: { workspace.run("tissue.constraint.remove",{target:panel.item.id,constraint:panel.focused}); panel.focused=""; } }
    }
}
