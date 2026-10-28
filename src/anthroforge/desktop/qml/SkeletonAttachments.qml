import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    required property var service
    property string chosen: ""
    readonly property var rows: (service.state.evidence || []).filter(r=>!service.state.selection || r.owner===service.state.selection).reduce((all,r)=>all.concat((r.after || []).map(p=>({owner:r.owner,name:r.name || r.owner,point:p,before:(r.before || []).find(b=>b.point===p.point)}))),[])
    readonly property var selected: rows.find(r=>r.owner+":"+r.point.point===chosen) || ({})
    RowLayout {
        Label { text: "Attachment locations"; color: Theme.text; font.bold: true }
        UiSearchChoice {
            Layout.fillWidth: true; choices: panel.rows.map(r=>Object.assign({},r,{name:r.name+" · "+r.point.point}))
            text: panel.selected.name || "Choose an attachment"
            onChosen: row=>{ panel.chosen=row.owner+":"+row.point.point; }
        }
    }
    Label {
        Layout.fillWidth: true; color: Theme.muted; wrapMode: Text.Wrap
        text: panel.selected.before ? "Before · "+panel.selected.before.position.map(n=>n.toFixed(4)).join(", ")+" m → "+panel.selected.point.role : "Choose a bound point to inspect or correct its placement"
    }
    RowLayout {
        VectorSetting {
            label: "Proposed world position"; length: true; live: false
            values: panel.selected.point?.position || [0,0,0]
            enabled: !!panel.selected.point && panel.selected.point.point!==panel.selected.owner || (!!panel.selected.point && panel.service.state.comparison?.rows?.find(r=>r.id===panel.selected.owner)?.after?.kind==="ANCHOR")
            onEdited: values=>panel.service.correctPlacement(panel.selected.owner,panel.selected.point,values)
        }
        UiButton { text: "Reset"; enabled: !!panel.selected.point; onClicked: panel.service.resetPlacement(panel.selected.owner,panel.selected.point.point) }
    }
}
