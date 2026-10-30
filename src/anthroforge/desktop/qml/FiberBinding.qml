import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    required property var curve
    required property var point
    readonly property var binding: (curve.bindings || []).find(b=>b.point===point.id) || null
    readonly property bool isFiber: curve.bindings !== undefined
    readonly property bool mandatory: binding && (!curve.closed ? (point.id===curve.points[0].id || point.id===curve.points[curve.points.length-1].id) : curve.bindings.length===1)
    visible: isFiber; Layout.fillWidth: true; spacing: Theme.gap
    Label { text: "Anatomical binding"; color: Theme.muted }
    SurfaceSelector {
        id: target; objectName: "fiberBindingTarget"; Layout.fillWidth: true
        target: panel.binding?.instance ? "mirror/" + panel.binding.instance + "/" + panel.binding.target : (panel.binding?.target || "")
        role: panel.binding?.role || ""
    }
    RowLayout {
        Layout.fillWidth: true
        UiButton { objectName: "setFiberBinding"; text: panel.binding ? "Rebind point" : "Bind point"; Layout.fillWidth: true; enabled: !!target.current.ready; onClicked: App.runtime.run("fiber.binding.set",{curve:panel.curve.id,point:panel.point.id,target:target.current.id,role:target.current.role}) }
        UiButton { objectName: "removeFiberBinding"; text: "Remove"; visible: !!panel.binding; enabled: !panel.mandatory; hint: panel.mandatory ? "Keep both open endpoints or one closed anchor bound" : "Remove this point's binding"; onClicked: App.runtime.run("fiber.binding.remove",{curve:panel.curve.id,point:panel.point.id}) }
    }
    UiCombo {
        objectName: "fiberBindingScope"; Layout.fillWidth: true
        visible: !!panel.binding
        model: ["Current parent", "Any eligible parent"]
        currentIndex: panel.binding?.capture_scope === "ANY_PARENT" ? 1 : 0
        hint: "Choose eligible surfaces when this bound point is edited"
        onActivated: App.runtime.run("fiber.binding.scope",{curve:panel.curve.id,point:panel.point.id,scope:currentIndex===1?"ANY_PARENT":"CURRENT_PARENT"})
    }
    MirrorSharing { visible: !!panel.binding; source: panel.curve.id || ""; binding: panel.point.id || "" }
    NumericSetting {
        objectName:"fiberPinNormalOffset"; visible:!!panel.binding?.attachment; label:"Normal Offset"; length:true
        value:panel.binding?.attachment?.binding?.[17] || 0
        hint:"Signed surface-normal distance at this retained material point; preserves its target"
        onEdited:value=>App.runtime.run("fiber.binding.offset",{curve:panel.curve.id,point:panel.point.id,value:value})
    }
}
