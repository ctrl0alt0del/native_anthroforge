import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    required property string target
    required property string part
    required property string side
    required property var inflation
    property var draft: null
    property var resolved: ({})
    property string resetKind: ""
    readonly property bool editing: draft !== null
    readonly property var values: Object.assign({}, inflation, resolved, draft || {})
    readonly property var preview: workspace.tissuePreview
    readonly property string selection: target + ":" + part + ":" + side
    Layout.fillWidth: true; spacing: Theme.gap
    onSelectionChanged: if(editing) cancel()
    onPreviewChanged: {
        if(editing && preview.target===target && preview.part===part && preview.side===side && preview.state==="ready") {
            resolved=preview.settings;
            if(resetKind) { const value=Object.assign({},draft); const key=resetKind==="PROFILE" ? "profile" : "control"; value[key]=resolved[key]; draft=value; resetKind=""; }
        }
    }
    function request(reset) {
        if(reset) resetKind=reset;
        return workspace.run("tissue.preview",{target:target,part:part,side:side,changes:draft,reset:resetKind});
    }
    function edit(key,value) {
        const changes=Object.assign({},draft || {}); changes[key]=value;
        if(editing) { draft=changes; request(""); }
        else workspace.run("tissue.inflation",{target:target,part:part,side:side,changes:changes});
    }
    function reset(kind) {
        if(editing) request(kind);
        else workspace.run(kind==="PROFILE" ? "tissue.profile.reset" : "tissue.control.reset",{target:target,part:part,side:side});
    }
    function start() { resolved={}; draft={}; if(!request("")) draft=null; }
    function cancel() { draft=null; resolved={}; resetKind=""; workspace.run("tissue.preview.cancel",{}); }
    function accept() {
        workspace.run("tissue.preview.accept",{token:preview.token});
        if(workspace.tissuePreview.state==="idle") { draft=null; resolved={}; resetKind=""; }
    }
    RowLayout {
        Layout.fillWidth: true
        UiButton { objectName: "tissuePreviewStart"; visible: !panel.editing; text: "Preview inflation edits"; Layout.fillWidth: true; onClicked: panel.start() }
        UiButton { objectName: "tissuePreviewAccept"; visible: panel.editing; text: "Accept"; primary: true; Layout.fillWidth: true; enabled: panel.preview.state==="ready"; onClicked: panel.accept() }
        UiButton { objectName: "tissuePreviewCancel"; visible: panel.editing; text: "Cancel"; Layout.fillWidth: true; onClicked: panel.cancel() }
    }
    Label {
        visible: panel.editing; Layout.fillWidth: true; wrapMode: Text.WordWrap
        text: "Inflated rest preview · " + panel.preview.state
        color: Theme.accent
        ToolTip.visible: hovered.hovered; ToolTip.text: "Shows inflation before relaxation, cropping and stacking. The document changes only when accepted."
        HoverHandler { id: hovered }
    }
    Label { visible: panel.editing && !!panel.preview.error; text: panel.preview.error || ""; Layout.fillWidth: true; wrapMode: Text.WordWrap; color: Theme.muted }
}
