import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    required property var service
    readonly property var selected: service.references.find(r=>r.key===service.state.reference) || ({})
    readonly property var matches: service.targets.filter(r=>r.name.toLowerCase().includes(targetSearch.text.toLowerCase()))
    spacing: Theme.gap
    Label { text: "External references"; color: Theme.text; font.bold: true }
    UiField { id: referenceSearch; Layout.fillWidth: true; placeholderText: "Search references" }
    ListView {
        objectName: "assemblyReferences"
        Layout.fillWidth: true; Layout.preferredHeight: 130; clip: true; reuseItems: true
        model: panel.service.references.filter(r=>(r.name+" "+r.relationship).toLowerCase().includes(referenceSearch.text.toLowerCase()))
        ScrollBar.vertical: ScrollBar {}
        delegate: UiButton {
            required property var modelData
            width: ListView.view.width-14; height: 40; alignLeft: true
            text: modelData.name+" · "+modelData.relationship+" · "+(modelData.action==="map" ? "Mapped" : modelData.action==="detach" ? "World" : "Unresolved")
            checked: modelData.key===panel.service.state.reference
            hint: modelData.name+"\n"+modelData.role
            onClicked: panel.service.selectReference(modelData.key)
        }
        Label { anchors.centerIn: parent; text: "No external references"; color: Theme.muted; visible: !parent.count }
    }
    Label {
        Layout.fillWidth: true; Layout.preferredHeight: 34; color: Theme.text; wrapMode: Text.Wrap
        text: panel.selected.name ? panel.selected.name+" · "+(panel.selected.role || panel.selected.relationship) : "Choose a reference to map"
    }
    RowLayout {
        UiButton { text: "Include source"; enabled: !!panel.selected.key && !panel.service.state.repair; onClicked: panel.service.action("include"); hint: "Copy this source and its required construction" }
        UiButton { text: "Resolve later"; enabled: !!panel.selected.key && panel.selected.relationship!=="parent"; onClicked: panel.service.action("later") }
        UiButton { text: "Detach to world"; enabled: panel.selected.relationship==="parent"; onClicked: panel.service.action("detach") }
    }
    UiField { id: targetSearch; Layout.fillWidth: true; placeholderText: "Search destination objects"; enabled: !!panel.selected.key }
    ListView {
        objectName: "assemblyTargets"
        Layout.fillWidth: true; Layout.fillHeight: true; Layout.minimumHeight: 95; clip: true; reuseItems: true
        model: panel.matches
        ScrollBar.vertical: ScrollBar {}
        delegate: UiButton {
            required property var modelData
            width: ListView.view.width-14; alignLeft: true
            text: modelData.name; checked: panel.selected.target===modelData.target && (panel.selected.target_instance || "")===(modelData.instance || "")
            onClicked: panel.service.selectTarget(modelData)
        }
    }
    UiCombo {
        Layout.fillWidth: true; visible: !!panel.selected.property
        model: panel.service.properties; textRole: "name"; currentIndex: -1
        displayText: currentIndex<0 ? "Choose a matching numerical property" : currentText
        onActivated: index=>panel.service.mapTarget(panel.service.properties[index].property)
    }
    UiCheck {
        objectName: "assemblyRebind"; text: "Rebind to proposed exterior locations"
        enabled: panel.selected.action==="map" && panel.selected.relationship==="support"
        checked: !!panel.selected.rebind
        onClicked: panel.service.action("rebind")
        hint: "Use new attachment locations only after reviewing the evidence below"
    }
}
