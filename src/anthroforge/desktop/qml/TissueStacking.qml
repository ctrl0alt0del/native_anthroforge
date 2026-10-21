import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiSection {
    id: panel
    required property var item
    property string focused: ""
    readonly property var candidates: { const revision=workspace.state.revision; return workspace.stackingTissues().filter(o=>o.id!==item.id); }
    readonly property var filtered: candidates.filter(o=>o.name.toLowerCase().includes(search.text.toLowerCase()))
    readonly property var other: candidates.find(o=>o.id===focused) || ({})
    readonly property string side: ownSide.currentText || "a"
    readonly property string otherSide: supportSide.currentText || "a"
    readonly property var intent: item.stack_relationships?.find(r=>r.other===focused && r.side===side && r.other_side===otherSide)
    readonly property var evidence: item.stack_plan?.orders?.find(r=>(r.first===focused || r.second===focused))
    title: "Stacking"; expanded: false
    hint: "Surface tissues opt into stacking. Provider surfaces are evaluated first; final geometry remains distinct from intrinsic inflation."
    function configure(key,value) { const changes={}; changes[key]=value; workspace.run("tissue.stacking.configure",{target:item.id,changes:changes}); }
    function saveIntent() {
        workspace.run("tissue.stacking.relationship",{target:item.id,other:focused,side:side,other_side:otherSide,mode:orderMode.currentText,cover:coverMode.currentIndex===0?"SELF":"OTHER",excluded:exclude.checked});
        orderMode.currentIndex=Qt.binding(()=>Math.max(0,orderMode.model.indexOf(panel.intent?.mode)));
        coverMode.currentIndex=Qt.binding(()=>panel.intent?.cover==="OTHER"?1:0);
        exclude.checked=Qt.binding(()=>panel.intent?.excluded || false);
    }
    function editRegion() { workspace.tissueRegionTools.begin({other:focused,side:side,other_side:otherSide,mode:orderMode.currentText,cover:coverMode.currentIndex===0?"SELF":"OTHER",excluded:false}); }
    UiCheck { objectName: "tissueStackingEnabled"; text: "Enable stacking"; checked: panel.item.stacking || false; onClicked: workspace.run("tissue.configure",{target:panel.item.id,changes:{stacking:checked}}) }
    UiSection {
        title: "Stacking settings"; expanded: false
        NumericSetting { objectName: "tissueStackClearance"; label: "Clearance"; length: true; value: panel.item.stack_settings?.clearance || 0; onEdited: value=>panel.configure("clearance",value) }
        NumericSetting { label: "Search distance"; length: true; value: panel.item.stack_settings?.search || 0; onEdited: value=>panel.configure("search",value) }
        NumericSetting { label: "Smoothing radius"; length: true; value: panel.item.stack_settings?.radius || 0; onEdited: value=>panel.configure("radius",value) }
        NumericSetting { label: "Smoothing strength"; value: panel.item.stack_settings?.strength || 0; onEdited: value=>panel.configure("strength",value) }
        NumericSetting { label: "Blend distance"; length: true; value: panel.item.stack_settings?.blend || 0; onEdited: value=>panel.configure("blend",value) }
        NumericSetting { label: "Shape preservation"; value: panel.item.stack_settings?.preservation || 100; onEdited: value=>panel.configure("preservation",value) }
        NumericSetting { label: "Maximum adjustment"; length: true; value: panel.item.stack_settings?.adjustment || 0; onEdited: value=>panel.configure("adjustment",value) }
    }
    UiField { id: search; objectName: "tissueStackSearch"; Layout.fillWidth: true; placeholderText: "Find a tissue…" }
    ListView {
        id: list; objectName: "tissueStackList"; Layout.fillWidth: true
        Layout.preferredHeight: Math.min(160,count*32); clip: true; reuseItems: true
        model: panel.filtered; ScrollBar.vertical: ScrollBar {}
        delegate: UiButton {
            required property var modelData
            objectName: "tissueStackChoice_"+modelData.id
            width: list.width; height: 32; flatStyle: true; alignLeft: true
            text: modelData.name+(modelData.enabled?"":" · disabled"); checkable: true; checked: panel.focused===modelData.id
            onClicked: panel.focused=modelData.id
        }
    }
    Label { visible: panel.candidates.length===0; text: "Create another surface tissue to define a relationship."; color: Theme.muted; Layout.fillWidth: true; wrapMode: Text.WordWrap }
    ColumnLayout {
        visible: !!panel.other.id; Layout.fillWidth: true; spacing: Theme.gap
        RowLayout {
            Layout.fillWidth: true
            UiCombo { id: ownSide; Layout.fillWidth: true; model: panel.item.both_sides?["a","b"]:["a"]; hint: "This tissue side" }
            UiCombo { id: supportSide; Layout.fillWidth: true; model: panel.other.both_sides?["a","b"]:["a"]; hint: "Other tissue side" }
        }
        UiCombo { id: orderMode; objectName: "tissueStackOrder"; Layout.fillWidth: true; model: ["AUTO","REQUESTED","EXPLICIT"]; currentIndex: Math.max(0,model.indexOf(panel.intent?.mode)); hint: "Requested order must agree with geometry; explicit order still requires validation."; onActivated: panel.saveIntent() }
        UiCombo { id: coverMode; objectName: "tissueStackCover"; Layout.fillWidth: true; visible: orderMode.currentIndex>0; model: ["This tissue covers","Other tissue covers"]; currentIndex: panel.intent?.cover==="OTHER"?1:0; onActivated: panel.saveIntent() }
        UiCheck { id: exclude; objectName: "tissueStackExclude"; text: "Exclude this pair"; checked: panel.intent?.excluded || false; onClicked: panel.saveIntent() }
        Label { visible: !!panel.intent?.regions?.length; text: "Selected support region · "+(panel.intent?.regions?.length || 0)+" faces"; color: Theme.muted }
        UiButton { objectName: "tissueStackRegion"; text: "Select support footprint"; Layout.fillWidth: true; enabled: orderMode.currentIndex>0 && !exclude.checked; hint: "Choose Requested or Explicit order, then select material faces on the covering tissue"; onClicked: panel.editRegion() }
        ColumnLayout {
            visible: workspace.tissueRegionTools.state.active; Layout.fillWidth: true
            Label { text: "Click covering faces to toggle the draft footprint."; color: Theme.muted; Layout.fillWidth: true; wrapMode: Text.WordWrap }
            UiNotice { active: panel.visible && workspace.tissueRegionTools.state.active; text: workspace.tissueRegionTools.state.error || ""; error: true }
            UiButton { text: "Use entire footprint"; Layout.fillWidth: true; onClicked: workspace.tissueRegionTools.clear() }
            RowLayout {
                Layout.fillWidth: true
                UiButton { objectName: "tissueStackRegionAccept"; text: "Accept region"; enabled: !workspace.tissueRegionTools.state.error; Layout.fillWidth: true; onClicked: workspace.tissueRegionTools.accept() }
                UiButton { objectName: "tissueStackRegionCancel"; text: "Cancel"; onClicked: workspace.tissueRegionTools.cancel() }
            }
        }
        RowLayout {
            Layout.fillWidth: true
            UiButton { objectName: "tissueStackRemove"; text: "Reset relationship"; glyph: "delete"; hint: "Remove overrides and restore automatic behavior"; enabled: !!panel.intent; onClicked: workspace.run("tissue.stacking.remove",{target:panel.item.id,other:panel.focused,side:panel.side,other_side:panel.otherSide}) }
        }
        UiNotice { active: panel.visible && !!panel.evidence; text: panel.evidence?.covering ? (panel.evidence.covering===panel.item.id?"This tissue covers the selected tissue":"The selected tissue covers this tissue") : "No accepted stacking order" }
    }
    UiNotice { active: panel.visible; text: panel.item.stack_plan?.error || ""; error: true }
}
