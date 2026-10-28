import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: section
    required property var adapter
    readonly property var selected: adapter.state
    readonly property var settings: selected.report?.settings || ({})
    property real previewValue: 0
    Layout.fillWidth: true
    Label { text: "Fitted shortcuts"; color: Theme.text; font.bold: true; Layout.topMargin: Theme.gap }
    Label { visible: fits.count===0; text: "Select a shortcut and choose Fit to bones to save a fitted skin."; color: Theme.muted; wrapMode: Text.Wrap; Layout.fillWidth: true }
    UiField { Layout.fillWidth: true; placeholderText: "Search fitted shortcuts"; onTextChanged: section.adapter.search(text) }
    ListView {
        id: fits; objectName: "skinFits"; model: section.adapter.results; Layout.fillWidth: true
        Layout.preferredHeight: Math.min(180, Math.max(36, count*36)); clip: true
        ScrollBar.vertical: ScrollBar {}
        delegate: ItemDelegate {
            required property string key
            required property string label
            required property bool stale
            width: ListView.view.width; height: 36
            highlighted: key===section.selected.id
            contentItem: Label { text: label+(stale ? " · Outdated" : ""); color: Theme.text; elide: Text.ElideRight }
            background: Rectangle { color: parent.highlighted ? Theme.hover : parent.hovered ? Theme.hover : "transparent" }
            onClicked: { section.adapter.select(key); section.previewValue=section.settings.minimum || 0; }
        }
    }
    ColumnLayout {
        visible: !!section.selected.id; Layout.fillWidth: true
        Label { text: "Preview saved fit"; color: Theme.text }
        UiQuantityField {
            objectName: "skinFitPreviewValue"; Layout.fillWidth: true
            dimension: section.selected.report?.dimension || "SCALAR"; canonicalValue: section.previewValue
            onCanonicalEdited: value => { section.previewValue=value; section.adapter.preview(value); }
        }
        Slider {
            Layout.fillWidth: true; from: section.settings.minimum ?? 0; to: section.settings.maximum ?? 1
            value: section.previewValue
            onMoved: { section.previewValue=value; section.adapter.preview(value); }
        }
        RowLayout {
            UiButton { text: "Show preview"; onClicked: section.adapter.preview(section.previewValue) }
            UiButton { text: "Hide preview"; onClicked: section.adapter.hide() }
        }
        RowLayout {
            UiButton { text: "Refit"; enabled: section.adapter.refitEligibility.available; hint: section.adapter.refitEligibility.reason; onClicked: section.adapter.refit() }
            UiButton { text: "Delete fit"; onClicked: section.adapter.remove() }
        }
        Label { text: "Saved snapshot; playback does not recalculate anatomy."; color: Theme.muted; wrapMode: Text.Wrap; Layout.fillWidth: true }
        UiSection {
            title: "Fit accuracy"; Layout.fillWidth: true
            UiDetail { label:"Active bones"; value:String(section.selected.report?.active_bones ?? "—") }
            UiDetail { label:"Moving region · worst held-out 95% error"; value:section.selected.report?.moving_validation_p95 == null ? "Unavailable" : Number(section.selected.report.moving_validation_p95).toPrecision(3)+"% of height" }
            Label { text: "Error at sampled values, relative to the captured skin. Held-out samples were not used to fit bones."; color: Theme.muted; wrapMode: Text.Wrap; Layout.fillWidth: true }
            Repeater {
                model: section.selected.report?.rows || []
                UiDetail {
                    required property var modelData
                    label: Number(modelData.value).toPrecision(4)+(modelData.training ? " · Training" : " · Held-out")
                    value: "95% error · whole skin: "+Number(modelData.p95_percent_height).toPrecision(3)+"% · moving region: "+Number(modelData.moving_p95_percent_height).toPrecision(3)+"% of height"
                }
            }
        }
    }
}
