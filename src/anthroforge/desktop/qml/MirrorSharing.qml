import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls

UiCheck {
    id: setting
    required property string source
    required property string binding
    text: "Use same target on both sides"
    hint: "Explicit midline support sharing; this never changes mirrored geometry"
    checked: { const revision=App.runtime.state.revision; return !!source && !!binding && App.mirrors.mirrorTargetShared(source,binding); }
    enabled: !App.selection.selectedData.readonly && !App.runtime.state.waiting
    onClicked: App.runtime.run("mirror.attachment.share",{source:source,binding:binding,enabled:checked})
}
