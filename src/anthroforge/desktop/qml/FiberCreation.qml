import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    objectName: "fiberCreation"
    required property var curve
    readonly property string sourceId: curve.id || ""
    property var overrides: ({})
    readonly property var rows: (curve.points || []).map((p,i)=>({id:p.id,index:i,name:"Point "+(i+1),mandatory:!curve.closed && (i===0 || i===curve.points.length-1)}))
    Layout.fillWidth: true; spacing: Theme.gap
    onSourceIdChanged: { overrides={}; allPoints.checked=false; search.text=""; }
    function binding(row) { return overrides[row.id] || {bound:row.mandatory || (curve.closed && row.index===0),target:"",role:""}; }
    function update(row, changes) { const next=Object.assign({},overrides); next[row.id]=Object.assign({},binding(row),changes); overrides=next; }
    function createFiber() {
        const bindings=rows.filter(r=>binding(r).bound).map(r=>({point:r.id,target:binding(r).target,role:binding(r).role}));
        App.construction.createConstruction("fiber.create",{curve:sourceId,bindings:bindings});
    }
    UiButton { objectName:"createFiberFromCurve"; property string sourceId: panel.sourceId; text:"Create Fiber"; Layout.fillWidth:true; enabled:!!panel.sourceId; hint:"Independent copy · endpoints bind to nearest SCP surfaces"; onClicked:panel.createFiber() }
    UiSection {
        title:"Fiber binding options"; expanded:false
        Label { text:panel.curve.closed ? "First point binds by default. Choose any additional anchors." : "Endpoints bind to nearest SCP surfaces. Override only where needed."; color:Theme.muted; Layout.fillWidth:true; wrapMode:Text.WordWrap }
        UiCheck { id:allPoints; objectName:"fiberAllPoints"; text:"Show all points"; hint:"Add or remove optional anatomical bindings" }
        UiField { id:search; objectName:"fiberPointSearch"; placeholderText:"Find a point…"; Layout.fillWidth:true }
        ListView {
            id:list; objectName:"fiberBindingList"; Layout.fillWidth:true
            Layout.preferredHeight:Math.min(300,count*128); clip:true; reuseItems:true
            model:panel.rows.filter(r=>(allPoints.checked || panel.binding(r).bound) && r.name.toLowerCase().includes(search.text.toLowerCase()))
            ScrollBar.vertical:ScrollBar {}
            delegate:ColumnLayout {
                id:row; required property var modelData
                width:list.width; height:128
                UiCheck { text:row.modelData.name; checked:panel.binding(row.modelData).bound; enabled:!row.modelData.mandatory; onClicked:panel.update(row.modelData,{bound:checked}) }
                SurfaceSelector {
                    objectName:"fiberCreationSurface"; property string sourceId:panel.sourceId
                    automatic:true; enabled:panel.binding(row.modelData).bound
                    target:panel.binding(row.modelData).target; role:panel.binding(row.modelData).role
                    onActivated:surface=>panel.update(row.modelData,{target:surface.id,role:surface.role})
                }
            }
        }
    }
}
