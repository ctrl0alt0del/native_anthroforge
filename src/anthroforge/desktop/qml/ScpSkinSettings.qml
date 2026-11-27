import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiSection {
    id: section
    required property var source
    readonly property var settings: source.settings || ({})
    readonly property var draft: source.draft || ({})
    readonly property var limb: settings.limb
    readonly property var modes: ["INHERIT", "FOLLOW", "FILL"]
    title: "Draft skin"; stateKey: "scp/draftSkin"; expanded: false
    visible: source.scp === true && App.skinPanel.state.draft_settings?.backend === "AVBD"
    enabled: source.editable === true
    function change(key, value) {
        const values = {}; values[key] = value;
        App.runtime.run("skin.contributor.configure", {owner:source.owner, values:values})
    }
    function radius(key, value) {
        const patch = {}; patch[key] = value; change("limb", patch)
    }
    UiCombo {
        objectName: "scpSkinMode"; Layout.fillWidth: true
        model: ["Inherit", "Follow SCP", "Fill Region"]
        currentIndex: section.modes.indexOf(section.settings.build_mode || "INHERIT")
        onActivated: section.change("build_mode", section.modes[currentIndex])
    }
    Label {
        visible: section.settings.build_mode === "INHERIT"
        text: (section.draft.mode === "FILL" ? "Fill Region" : "Follow SCP") +
              (section.draft.mode_source ? " from " + section.draft.mode_source : " (root default)")
        color: Theme.muted; Layout.fillWidth: true; wrapMode: Text.Wrap
    }
    Label {
        visible: section.draft.mode === "FILL"
        text: "Fill Region is saved. Building this region still requires compartment inputs."
        color: Theme.muted; wrapMode: Text.Wrap; Layout.fillWidth: true
    }
    UiButton {
        visible: section.draft.child === true
        objectName: "scpSkinLimb"; text: section.limb ? "Remove limb" : "Start limb here"
        onClicked: section.change("limb", section.limb ? null : ({}))
    }
    Label {
        visible: !section.limb && !!section.draft.limb_source
        text: "Limb from " + (section.draft.limb_source || ""); color: Theme.muted
    }
    Repeater {
        model: section.limb ? [{key:"rest_radius",label:"Material radius",autoValue:section.draft.auto_rest},
                               {key:"boundary_radius",label:"Boundary radius",autoValue:section.draft.auto_boundary}] : []
        ColumnLayout {
            required property var modelData
            readonly property bool automatic: section.limb?.[modelData.key] == null
            Layout.fillWidth: true
            UiCombo {
                model: [modelData.label + " · Auto", modelData.label + " · Manual"]
                currentIndex: automatic ? 0 : 1; Layout.fillWidth: true
                onActivated: if (!currentIndex) section.radius(modelData.key, null)
                             else if (modelData.autoValue > 0) section.radius(modelData.key, modelData.autoValue)
                             else manualInput.focusValue()
            }
            NumericSetting {
                id: manualInput; live: false; length: true; minimum: 0; decimals: 5
                label: automatic && !modelData.autoValue ? "Enter manual radius" : modelData.label
                value: section.limb?.[modelData.key] ?? modelData.autoValue ?? 0
                onEdited: value => { if (value > 0) section.radius(modelData.key, value) }
            }
        }
    }
    Label {
        visible: !!section.limb && (section.limb.rest_radius == null || section.limb.boundary_radius == null) && !!section.draft.radius_reason
        text: section.draft.radius_reason || ""; wrapMode: Text.Wrap; Layout.fillWidth: true; color: Theme.muted
    }

}
