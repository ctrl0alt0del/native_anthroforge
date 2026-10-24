import QtQuick
import QtQuick.Controls

UiCheck {
    id: setting
    required property string source
    required property string binding
    text: "Use same target on both sides"
    hint: "Explicit midline support sharing; this never changes mirrored geometry"
    checked: { const revision=workspace.state.revision; return !!source && !!binding && workspace.mirrorTargetShared(source,binding); }
    enabled: !workspace.selectedData.readonly && !workspace.state.waiting
    onClicked: workspace.run("mirror.attachment.share",{source:source,binding:binding,enabled:checked})
}
