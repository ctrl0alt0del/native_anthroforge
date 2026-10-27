import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiDialog {
    id: dialog
    required property var adapter
    property real minimum: 0
    property real maximum: 1
    property int bones: 4
    property int samples: 9
    parent: Overlay.overlay
    anchors.centerIn: parent
    width: Math.min(420, parent ? parent.width - 32 : 420)
    modal: true
    title: "Fit shortcut to bones"
    standardButtons: Dialog.Cancel
    function initialize() {
        minimum = Number(adapter.fitEligibility.value || 0);
        maximum = minimum + (Math.abs(minimum) || 1);
        open();
    }
    contentItem: ColumnLayout {
        spacing: Theme.gap
        Label { text: "Sample this shortcut's range and create an independent bone-driven skin."; wrapMode: Text.Wrap; color: Theme.muted; Layout.fillWidth: true }
        RowLayout {
            Label { text: "Minimum"; color: Theme.text; Layout.fillWidth: true }
            UiQuantityField { objectName: "skinFitMinimum"; Layout.preferredWidth: 130; dimension: dialog.adapter.fitEligibility.dimension || "SCALAR"; canonicalValue: dialog.minimum; onCanonicalEdited: value => dialog.minimum=value }
        }
        RowLayout {
            Label { text: "Maximum"; color: Theme.text; Layout.fillWidth: true }
            UiQuantityField { objectName: "skinFitMaximum"; Layout.preferredWidth: 130; dimension: dialog.adapter.fitEligibility.dimension || "SCALAR"; canonicalValue: dialog.maximum; onCanonicalEdited: value => dialog.maximum=value }
        }
        NumericSetting { label: "Bones"; value: dialog.bones; minimum: 1; maximum: 64; decimals: 0; step: 1; onEdited: value => dialog.bones=value }
        NumericSetting { label: "Samples"; value: dialog.samples; minimum: 5; maximum: 33; decimals: 0; step: 2; hint: "Odd sample count; alternating samples check the fitted result."; onEdited: value => dialog.samples=value }
        Label { visible: !!dialog.adapter.fitEligibility.warnings?.length; text: (dialog.adapter.fitEligibility.warnings || []).join("\n"); color: Theme.muted; wrapMode: Text.Wrap; Layout.fillWidth: true }
        UiButton {
            objectName: "skinFitStart"; text: "Fit to bones"; Layout.fillWidth: true
            enabled: dialog.adapter.fitEligibility.available && dialog.maximum>dialog.minimum && dialog.samples%2===1
            hint: dialog.adapter.fitEligibility.reason || "Range must increase; sample count must be odd."
            onClicked: { dialog.adapter.fit({minimum:dialog.minimum,maximum:dialog.maximum,bones:dialog.bones,samples:dialog.samples}); dialog.close(); }
        }
    }
}
