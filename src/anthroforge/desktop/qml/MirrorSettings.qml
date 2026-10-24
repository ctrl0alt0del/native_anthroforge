import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiSection {
    id: panel
    title: "Mirror"
    property var selected: workspace.selectedData
    readonly property var settings: selected.mirror_settings || {}
    readonly property bool anatomical: !selected.is_construction && !selected.is_control
    visible: !!selected.id && !selected.mirror_source && selected.kind !== "IMAGE"
    enabled: !selected.readonly && !workspace.state.waiting
    function update(values) {
        const blockers=workspace.run("mirror.removal.inspect",Object.assign({target:selected.id},values));
        if (!blockers) return;
        if (blockers.length) { affected.show(blockers); return; }
        workspace.run("mirror.configure", Object.assign({target:selected.id}, values));
    }
    AffectedConsumersDialog { id: affected }
    UiCheck {
        objectName: "mirrorChildren"; text: "Mirror children"
        visible: panel.anatomical
        checked: panel.settings.enabled || false
        nextCheckState: function() { return checkState; }
        onClicked: panel.update({enabled:!panel.settings.enabled})
    }
    UiCheck {
        objectName: "mirrorPlaneOverride"; text: "Override inherited plane"
        visible: !panel.anatomical
        checked: panel.settings.override || false
        nextCheckState: function() { return checkState; }
        onClicked: panel.update({override:!panel.settings.override})
    }
    UiCheck {
        objectName: "mirrorInherit"; text: "Inherit parent mirror"
        checked: panel.settings.inherit !== false
        nextCheckState: function() { return checkState; }
        onClicked: panel.update({inherit:panel.settings.inherit === false})
    }
    RowLayout {
        Layout.fillWidth: true
        enabled: panel.settings.enabled || panel.settings.override || false
        Label { text: "Axis"; color: Theme.muted }
        UiCombo {
            objectName: "mirrorAxis"; Layout.fillWidth: true; model: ["X", "Y", "Z"]
            currentIndex: Math.max(0,model.indexOf(panel.settings.axis || "X"))
            onActivated: panel.update({axis:currentText})
        }
        UiNumberField {
            objectName: "mirrorShift"; Layout.fillWidth: true
            value: (panel.settings.shift || 0)/workspace.state.unit_factor
            step: .001/workspace.state.unit_factor
            Accessible.name: "Mirror plane shift"
            onEdited: number => panel.update({shift:number*workspace.state.unit_factor})
        }
    }
    UiCombo {
        objectName: "mirrorDisplay"; Layout.fillWidth: true
        model: ["Both sides", "Source only", "Mirror only"]
        currentIndex: Math.max(0,["BOTH","SOURCE","MIRROR"].indexOf(workspace.state.mirror_display || "BOTH"))
        onActivated: workspace.run("workspace.update",{mirror_display:["BOTH","SOURCE","MIRROR"][currentIndex]})
    }
}
