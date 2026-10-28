import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    required property var service
    UiField { id: search; Layout.fillWidth: true; placeholderText: "Search source bones" }
    ListView {
        objectName: "skeletonMatches"; Layout.fillWidth: true; Layout.fillHeight: true
        clip: true; reuseItems: true
        model: (panel.service.state.inventory || []).filter(r=>r.name.toLowerCase().includes(search.text.toLowerCase()))
        ScrollBar.vertical: ScrollBar {}
        delegate: ColumnLayout {
            required property var modelData
            width: ListView.view.width-14; spacing: 4
            readonly property string matched: panel.service.state.matches[modelData.source] || ""
            readonly property string added: panel.service.state.options.additions?.[modelData.source] || ""
            UiButton {
                Layout.fillWidth: true; text: modelData.name; alignLeft: true
                checked: panel.service.state.selection === parent.matched
                hint: modelData.reason; onClicked: panel.service.select(parent.matched || modelData.source)
            }
            RowLayout {
                Layout.fillWidth: true
                UiSearchChoice {
                    Layout.fillWidth: true; choices: panel.service.state.parents || []
                    text: choices.find(r=>r.id===parent.parent.matched)?.name || "Choose destination bone"
                    placeholder: "Search destination bones"
                    onChosen: row=>panel.service.match(modelData.source,row.id)
                }
                UiButton { text: "×"; hint: "Exclude this source bone"; onClicked: panel.service.match(modelData.source,"") }
            }
            UiSearchChoice {
                Layout.fillWidth: true; choices: panel.service.state.parents || []
                text: parent.added ? "Add under " + (choices.find(r=>r.id===parent.added)?.name || "") : "Or add as a new bone…"
                placeholder: "Choose destination parent for addition"
                onChosen: row=>panel.service.add(modelData.source,row.id)
            }
            Rectangle { Layout.fillWidth: true; implicitHeight: 1; color: Theme.border; Layout.topMargin: 4; Layout.bottomMargin: 6 }
        }
    }
}
