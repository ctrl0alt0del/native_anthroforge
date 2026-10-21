import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    required property string target
    required property string part
    property bool multipleParts: false
    Layout.fillWidth: true; spacing: Theme.gap
    function copy(source,destination) { workspace.run("tissue.side.copy",{target:target,part:part,source:source,destination:destination,all_parts:multipleParts && allParts.checked}); }
    UiCheck { id: allParts; objectName: "tissueCopyAllParts"; visible: panel.multipleParts; text: "Copy across all parts" }
    RowLayout {
        Layout.fillWidth: true
        UiButton { objectName: "tissueCopyAToB"; text: "Copy A → B"; Layout.fillWidth: true; hint: "Copy inflation and smoothing from side A to side B"; onClicked: panel.copy("a","b") }
        UiButton { objectName: "tissueCopyBToA"; text: "Copy B → A"; Layout.fillWidth: true; hint: "Copy inflation and smoothing from side B to side A"; onClicked: panel.copy("b","a") }
    }
}
