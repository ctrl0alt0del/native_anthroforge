import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: chooser
    property string target: ""
    property string role: ""
    property bool automatic: false
    property var selectedKey: null
    signal activated(var surface)
    readonly property var rows: { const revision=workspace.state.revision; return workspace.surfaceRoles(); }
    readonly property var chosen: rows.find(r=>selectedKey!==null ? r.key===selectedKey : r.id===target && r.role===role)
    readonly property var filtered: choices()
    readonly property var current: filtered[choice.currentIndex] || ({})
    Layout.fillWidth: true; spacing: Theme.gap
    onTargetChanged: selectedKey=null
    onRoleChanged: selectedKey=null
    function choices() {
        const found=rows.filter(r=>r.name.toLowerCase().includes(search.text.toLowerCase()));
        if(chosen && !found.some(r=>r.key===chosen.key)) found.unshift(chosen);
        return (automatic ? [{id:"",role:"",key:"",name:"Nearest SCP",ready:true}] : []).concat(found);
    }
    function synchronize() { choice.currentIndex=Qt.binding(()=>Math.max(0,filtered.findIndex(r=>r.key===(chosen?.key || "")))); }
    function activate(index) {
        const surface=filtered[index];
        selectedKey=surface.key;
        activated(surface);
        synchronize();
    }
    UiField { id: search; Layout.fillWidth: true; placeholderText: "Search anatomical surfaces"; Accessible.name: "Search anatomical surfaces" }
    UiCombo {
        id: choice; objectName: "surfaceRoleChoice"; Layout.fillWidth: true
        model: chooser.filtered; textRole: "name"; valueRole: "key"
        currentIndex: Math.max(0,chooser.filtered.findIndex(r=>r.key===(chooser.chosen?.key || "")))
        onModelChanged: Qt.callLater(chooser.synchronize)
        hint: "Choose an explicit surface role; unavailable roles are never substituted"
        onActivated: index=>chooser.activate(index)
    }
    Label { visible: !!chooser.current.id && !chooser.current.ready; text: chooser.current.reason || "This surface has no usable accepted output"; color: Theme.accent; Layout.fillWidth: true; wrapMode: Text.WordWrap }
}
