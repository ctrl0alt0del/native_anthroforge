import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

UiScrollView {
    id: inspector
    property var selected: workspace.selectedData
    readonly property var attachment: selected.attachment || {}
    readonly property var candidates: workspace.sceneChoices.parents
    readonly property bool dialogVisible: colorDialog.visible || constructionInspector.dialogVisible
    signal pickAnchor(string mode)
    signal deleteRequested(string entity)
    signal imageRequested(string parentId)
    clip: true; contentWidth: availableWidth
    function setAttachment(key, value) {
        const options = {entity:selected.id};
        options[key] = value;
        workspace.run("scp.attachment",options);
    }
    ColumnLayout {
        width: inspector.availableWidth; spacing: 12
        ColumnLayout {
            visible: !inspector.selected.id; Layout.fillWidth: true; Layout.topMargin: 45; spacing: 12
            Image { source: "icons/target.svg"; sourceSize: Qt.size(28,28); opacity: .4; Layout.alignment: Qt.AlignHCenter }
            Label { text: "Nothing selected"; font.pixelSize: 15; color: Theme.text; Layout.alignment: Qt.AlignHCenter }
            Label { text: "Select an object in the viewport or outliner to edit its properties."; color: Theme.muted; wrapMode: Text.WordWrap; horizontalAlignment: Text.AlignHCenter; Layout.fillWidth: true }
        }
        Label { visible: !!inspector.selected.readonly; text: inspector.selected.mirror_source ? "Mirrored instance · read-only" : "Outside this workspace · read-only"; color: Theme.accent; wrapMode: Text.WordWrap; Layout.fillWidth: true }
        UiButton {
            objectName: "selectMirrorSource"; text: "Select source"; Layout.fillWidth: true
            visible: !!inspector.selected.mirror_source
            onClicked: workspace.select(inspector.selected.mirror_source)
        }
        MirrorSettings { Layout.fillWidth: true }
        UiButton {
            objectName: "addObjectImage"; text: "Add reference image…"; glyph: "image"; Layout.fillWidth: true
            visible: !!inspector.selected.id && inspector.selected.kind !== "IMAGE"
            enabled: !inspector.selected.readonly && !workspace.state.waiting && !workspace.state.editing
            hint: "Import an image parented to this object; align it to the current orthographic axis view"
            onClicked: inspector.imageRequested(inspector.selected.id)
        }
        ColumnLayout {
            visible: !!inspector.selected.id && !inspector.selected.is_control && !inspector.selected.is_construction && !inspector.selected.is_tissue
            enabled: !inspector.selected.readonly && !workspace.state.waiting
            Layout.fillWidth: true; spacing: 10
            RowLayout {
                Image { source: inspector.selected.asset ? "icons/mesh.svg" : "icons/folder.svg"; sourceSize: Qt.size(19,19) }
                UiField {
                    id: nameField; objectName: "entityName"; Layout.fillWidth: true
                    Accessible.name: "Object name"
                    onAccepted: inspector.parent.forceActiveFocus()
                    Binding { target: nameField; property: "text"; when: !nameField.activeFocus; value: inspector.selected.name || "" }
                    onEditingFinished: if (inspector.selected.id && text !== inspector.selected.name) workspace.run("scp.rename",{entity:inspector.selected.id,name:text})
                }
            }
            Label { text: (inspector.selected.parent ? "Child SCP" : "Document root") + (inspector.selected.primitive ? "  ·  " + inspector.selected.primitive.kind : "  ·  Empty group"); color: Theme.muted; font.pixelSize: 11 }
            UiSection {
                title: "Transform"; objectName: "transformSection"
                Repeater {
                    model: ["Position · "+workspace.state.display_units, "Rotation · °", "Scale"]
                    delegate: ColumnLayout {
                        required property int index
                        required property string modelData
                        property int groupIndex: index
                        Layout.fillWidth: true; spacing: 5
                        Label { text: modelData; color: Theme.muted; font.pixelSize: 11 }
                        RowLayout {
                            spacing: 4
                            Repeater {
                                model: 3
                                delegate: UiNumberField {
                                    id: numericField
                                    required property int index
                                    property int component: groupIndex*3+index
                                    readonly property real unitFactor: groupIndex===0 ? workspace.state.unit_factor : 1
                                    objectName: "transform" + component
                                    Layout.fillWidth: true; Layout.preferredWidth: 65; Layout.minimumWidth: 50
                                    leftPadding: 23; rightPadding: 4
                                    Accessible.name: ["Position","Rotation","Scale"][groupIndex] + " " + ["X","Y","Z"][index]
                                    value: inspector.selected.trs ? Number(inspector.selected.trs[component])/unitFactor : 0
                                    step: groupIndex===0 ? .001/unitFactor : groupIndex===1 ? 1 : .01
                                    Text { x: 7; anchors.verticalCenter: parent.verticalCenter; text: ["X","Y","Z"][numericField.index]; color: Theme.axes[numericField.index]; font.pixelSize: 11; font.bold: true }
                                    onEdited: number => {
                                        if (!inspector.selected.trs) return;
                                        const values = inspector.selected.trs.slice();
                                        values[component] = number*unitFactor;
                                        workspace.run("scp.transform",{entity:inspector.selected.id,values:values});
                                    }
                                }
                            }
                        }
                    }
                }
            }
            UiSection {
                title: "Attachment"; visible: !!inspector.selected.parent
                Label { text: "Parent object"; color: Theme.muted; font.pixelSize: 11 }
                UiCombo {
                    Layout.fillWidth: true; model: inspector.candidates; textRole: "name"; valueRole: "id"
                    currentIndex: indexOfValue(inspector.selected.parent || "")
                    hint: "Changing parent preserves the current world pose"
                    onActivated: workspace.run("scp.reparent",{entity:inspector.selected.id,parent:currentValue})
                }
                Label { text: "Parent anchor"; color: Theme.muted; font.pixelSize: 11 }
                UiCombo {
                    Layout.fillWidth: true; model: ["Nearest surface", "Object origin"]
                    currentIndex: Math.max(0,["SURFACE_NEAREST","OBJECT_ORIGIN"].indexOf(inspector.attachment.parent_mode))
                    onActivated: inspector.setAttachment("parent_mode",["SURFACE_NEAREST","OBJECT_ORIGIN"][currentIndex])
                }
                Label { text: "Child anchor"; color: Theme.muted; font.pixelSize: 11 }
                UiCombo {
                    id: childMode; Layout.fillWidth: true; model: ["Face center", "Nearest vertex", "Object origin"]
                    property var codes: ["FACE_CENTER","VERTEX_NEAREST","OBJECT_ORIGIN"]
                    currentIndex: Math.max(0,codes.indexOf(inspector.attachment.child_mode))
                    onActivated: inspector.setAttachment("child_mode",codes[currentIndex])
                }
                RowLayout {
                    enabled: childMode.currentIndex !== 2
                    UiButton { text: "Pick anchor"; glyph: "target"; Layout.fillWidth: true; hint: "Click a face or vertex on this child in the viewport"; onClicked: inspector.pickAnchor(childMode.codes[childMode.currentIndex]) }
                    UiButton { text: "Clear"; hint: "Remove permanent face and vertex locks"; onClicked: workspace.run("scp.attachment",{entity:inspector.selected.id,face_lock:-1,vertex_lock:-1}) }
                }
                Label {
                    text: inspector.attachment.face_lock >= 0 ? "Locked to face " + inspector.attachment.face_lock : inspector.attachment.vertex_lock >= 0 ? "Locked to vertex " + inspector.attachment.vertex_lock : "Anchor chosen automatically"
                    color: Theme.muted; font.pixelSize: 11
                }
                UiCheck { text: "Follow parent rotation"; checked: inspector.attachment.follow_rotation || false; onClicked: inspector.setAttachment("follow_rotation",checked) }
                UiCombo {
                    Layout.fillWidth: true; model: ["Automatic rotation", "Stable surface", "Deformation flow"]
                    currentIndex: Math.max(0,["AUTO","STABLE_SURFACE","DEFORMATION_FLOW"].indexOf(inspector.attachment.strategy))
                    onActivated: inspector.setAttachment("strategy",["AUTO","STABLE_SURFACE","DEFORMATION_FLOW"][currentIndex])
                }
                RowLayout {
                    UiButton { text: "Recapture"; Layout.fillWidth: true; hint: "Rebuild the attachment from the current pose"; onClicked: workspace.run("scp.recapture",{entity:inspector.selected.id}) }
                    UiButton { text: "Origin to anchor"; hint: "Move the origin while preserving mesh position"; onClicked: workspace.run("scp.origin",{entity:inspector.selected.id}) }
                }
            }
            PrimitiveInspector { visible: !!inspector.selected.primitive }
            UiSection {
                title: "Display & evaluation"; expanded: false
                RowLayout {
                    Rectangle { implicitWidth: 24; implicitHeight: 24; radius: 4; color: inspector.selected.color || "#72b8ad"; border.color: Theme.border }
                    UiButton { text: "Object color…"; Layout.fillWidth: true; onClicked: { colorDialog.selectedColor = inspector.selected.color; colorDialog.open(); } }
                }
                Label { text: "Update mode"; color: Theme.muted; font.pixelSize: 11 }
                UiCombo {
                    Layout.fillWidth: true; model: ["Use project setting", "Live", "On release", "Manual"]
                    currentIndex: Math.max(0,["INHERIT","LIVE","ON_RELEASE","MANUAL"].indexOf(inspector.selected.update_mode))
                    onActivated: workspace.run("update_mode",{entity:inspector.selected.id,mode:["INHERIT","LIVE","ON_RELEASE","MANUAL"][currentIndex]})
                }
            }
            RowLayout {
                Layout.fillWidth: true
                UiButton { text: "Duplicate"; Layout.fillWidth: true; hint: "Create an independent copy"; onClicked: workspace.run("scp.duplicate",{entity:inspector.selected.id}) }
                UiButton { text: "Delete"; hint: "Delete this SCP, preserving children"; onClicked: inspector.deleteRequested(inspector.selected.id) }
            }
        }
        ControlInspector { onDeleteRequested: entity => inspector.deleteRequested(entity); visible: !!inspector.selected.is_control; enabled: !inspector.selected.readonly && !workspace.state.waiting }
        ConstructionInspector { id: constructionInspector; onDeleteRequested: entity => inspector.deleteRequested(entity); visible: !!inspector.selected.is_construction; enabled: !inspector.selected.readonly && !workspace.state.waiting }
        TissueInspector { visible: !!inspector.selected.is_tissue; enabled: !inspector.selected.readonly && !workspace.state.waiting }
        DependencyInspector { visible: !!inspector.selected.id }
        UiNotice { text: inspector.selected.error || ""; error: true }
        Item { implicitHeight: 8 }
    }
    ColorDialog { id: colorDialog; title: "Object color"; onAccepted: workspace.run("scp.color",{entity:inspector.selected.id,value:selectedColor.toString()}) }
}
