import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: header
    objectName: "inspectorHeader"
    readonly property var selected: App.selection.selectedData
    readonly property string category: selected.is_tissue ? "TISSUE" : selected.kind || (selected.is_control ? "CONTROL" : "SCP")
    property string page: "Shape"
    property bool shortcuts: page === "Shortcuts"
    onShortcutsChanged: if(shortcuts !== (page==="Shortcuts")) choose(shortcuts ? "Shortcuts" : "Shape")
    onPageChanged: shortcuts=page==="Shortcuts"
    onCategoryChanged: if(page!=="Skin") page=App.workbench.page(category)
    Component.onCompleted: page=App.workbench.page(category)
    function choose(value) { page=value; App.workbench.setPage(category,value); }
    Connections { target: App.shortcutPanel; function onRevealRequested() { header.choose("Shortcuts"); } }
    Layout.fillWidth: true; spacing: 5
    Label {
        objectName:"inspectorObjectTitle"; visible:!!header.selected.id; text:header.selected.name || ""; color:Theme.text; font.pixelSize:16; font.bold:true
        Layout.fillWidth:true; wrapMode:Text.Wrap; maximumLineCount:2; elide:Text.ElideRight
        Layout.leftMargin:Theme.inset; Layout.rightMargin:Theme.inset; Layout.topMargin:Theme.inset
        HoverHandler { id:nameHover }
        ToolTip.visible:nameHover.hovered && truncated; ToolTip.text:text; ToolTip.delay:500
    }
    Label { text:DisplayNames.label(header.category)+(header.selected.readonly ? " · Read-only" : ""); visible:!!header.selected.id; color:Theme.muted; Layout.fillWidth:true; Layout.leftMargin:Theme.inset; Layout.rightMargin:Theme.inset }
    UiButton { objectName:"selectMirrorSource"; text:"Select source"; visible:!!header.selected.mirror_source; Layout.fillWidth:true; Layout.leftMargin:Theme.inset; Layout.rightMargin:Theme.inset; onClicked:App.selection.select(header.selected.mirror_source) }
}
