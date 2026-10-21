import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    property var binding: ({})
    readonly property var settings: binding.shrinkwrap || ({})
    Layout.fillWidth: true
    function set(key,value) { const args={binding:binding.id}; args[key]=value; authoring.edit("shrinkwrap.update",args); }
    SurfaceSelector {
        target: panel.settings.surface?.target || ""
        role: panel.settings.surface?.role || ""
        onActivated: surface => panel.set("surface",{target:surface.id,role:surface.role})
    }
    Label { text: "Nearest surface point"; color: Theme.muted }
    UiCombo {
        Layout.fillWidth: true
        model: ["On surface","Inside","Outside","Outside surface"]
        readonly property var modes: ["ON_SURFACE","INSIDE","OUTSIDE","OUTSIDE_SURFACE"]
        currentIndex: modes.indexOf(panel.settings.mode)
        onActivated: panel.set("mode",modes[currentIndex])
    }
    NumericSetting { objectName:"shrinkwrapOffset"; label: "Offset · target local"; length: true; value: panel.settings.offset || 0; onEdited: value=>panel.set("offset",value) }
}
