import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: chooser
    property string target: ""
    property string role: ""
    property bool automatic: false
    signal activated(var surface)
    readonly property var rows: { const revision=workspace.state.revision; return workspace.surfaceRoles(); }
    readonly property var filtered: (automatic ? [{id:"",role:"",key:"",name:"Nearest SCP",ready:true}] : []).concat(rows.filter(r=>r.name.toLowerCase().includes(search.text.toLowerCase())))
    readonly property var current: filtered[choice.currentIndex] || ({})
    Layout.fillWidth: true; spacing: Theme.gap
    UiField { id: search; Layout.fillWidth: true; placeholderText: "Search anatomical surfaces"; Accessible.name: "Search anatomical surfaces" }
    UiCombo {
        id: choice; objectName: "surfaceRoleChoice"; Layout.fillWidth: true
        model: chooser.filtered; textRole: "name"; valueRole: "key"
        currentIndex: Math.max(0,chooser.filtered.findIndex(r=>r.id===chooser.target && r.role===chooser.role))
        hint: "Choose an explicit surface role; unavailable roles are never substituted"
        onActivated: chooser.activated(chooser.current)
    }
    Label { visible: !!chooser.current.id && !chooser.current.ready; text: chooser.current.reason || "This surface has no usable accepted output"; color: Theme.accent; Layout.fillWidth: true; wrapMode: Text.WordWrap }
}
