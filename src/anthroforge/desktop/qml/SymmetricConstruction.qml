import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiSection {
    id: panel
    title: "Symmetric construction"; expanded:false; stateKey:"curve/symmetry"
    required property var curve
    property bool topologyLocked: false
    readonly property string curveId: curve.id || ""
    property var plane: ({axis:"X",shift:0,rule:""})
    visible: !!curveId && (!curve.closed || !!curve.symmetric)
    onCurveIdChanged: plane=curve.symmetric || App.mirrors.defaultMirrorPlane(curveId)
    MirrorPlaneFields {
        definition: panel.plane; enabled: !panel.curve.symmetric
        onEdited: value=>panel.plane=value
    }
    UiButton {
        objectName: "createSymmetricLoop"; text: panel.curve.symmetric ? "Symmetric loop" : "Create symmetric loop"
        enabled: !panel.topologyLocked && !panel.curve.symmetric && !App.selection.selectedData.readonly
        Layout.fillWidth: true
        hint: "Use this authored half-path; both endpoints must lie on the chosen plane"
        onClicked: App.runtime.run("mirror.loop.create",Object.assign({curve:panel.curveId},panel.plane))
    }
    UiButton {
        objectName: "createMirroredRowSurface"; text: "Create mirrored-row surface"
        visible: !panel.curve.closed; Layout.fillWidth: true
        onClicked: App.construction.createConstruction("surface.create",{curves:[panel.curveId],kind:"LOFT",mirrored_rows:true,mirror_plane:panel.plane})
    }
}
