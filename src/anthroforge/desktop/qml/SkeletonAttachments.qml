import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    required property var service
    required property var review
    readonly property var viewState: service.state
    property string chosen: ""
    readonly property var rows: (panel.review.attachments || []).filter(r=>!panel.viewState.selection || r.owner===panel.viewState.selection)
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
            enabled: !!panel.selected.editable
            onEdited: values=>panel.service.correctPlacement(panel.selected.owner,panel.selected.point,values)
        }
        UiButton { text: "Reset"; enabled: !!panel.selected.point; onClicked: panel.service.resetPlacement(panel.selected.owner,panel.selected.point.point) }
    }
}
