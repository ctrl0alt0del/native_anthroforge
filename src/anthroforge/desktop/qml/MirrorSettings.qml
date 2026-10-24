import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiSection {
    id: panel
    title: "Mirror"
    property var selected: workspace.selectedData
    readonly property var settings: selected.mirror_settings || {}
    visible: !!selected.id && !selected.mirror_source && (!selected.is_construction || selected.is_tissue)
    enabled: !selected.readonly && !workspace.state.waiting
    function update(values) {
        workspace.run("mirror.configure", Object.assign({target:selected.id}, values));
    }
    UiCheck {
        objectName: "mirrorChildren"; text: "Mirror children"
        checked: panel.settings.enabled || false
        onClicked: panel.update({enabled:checked})
    }
    UiCheck {
        objectName: "mirrorInherit"; text: "Inherit parent mirror"
        checked: panel.settings.inherit !== false
        onClicked: panel.update({inherit:checked})
    }
    RowLayout {
        Layout.fillWidth: true
        enabled: panel.settings.enabled || false
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
