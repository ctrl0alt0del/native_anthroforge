import QtQuick
import QtQuick.Controls

ComboBox {
    id: control
    property string hint: ""
    implicitHeight: 28; implicitWidth: 150
    font.pixelSize: 12
    leftPadding: 9; rightPadding: 24
    hoverEnabled: true
    Accessible.name: hint || displayText
    ToolTip.visible: hovered && !!hint
    ToolTip.text: hint; ToolTip.delay: 500
    contentItem: Text { text: control.displayText; color: control.enabled ? Theme.text : Theme.muted; font: control.font; verticalAlignment: Text.AlignVCenter; elide: Text.ElideRight }
    indicator: Text { text: "⌄"; color: Theme.muted; x: control.width-19; y: 4; font.pixelSize: 15 }
    background: Rectangle { radius: 4; color: Theme.field; border.color: control.activeFocus ? Theme.accent : Theme.border }
    delegate: ItemDelegate {
        required property int index
        width: control.width; height: 29
        text: control.textAt(index)
        font.pixelSize: 12
        highlighted: control.highlightedIndex === index
        contentItem: Text { text: parent.text; font: parent.font; color: Theme.text; verticalAlignment: Text.AlignVCenter; elide: Text.ElideRight }
        background: Rectangle { color: parent.highlighted ? Theme.selection : Theme.panel }
    }
    popup: Popup {
        y: control.height + 3; width: control.width
        implicitHeight: Math.min(contentItem.implicitHeight + 8, 330); padding: 4
        background: Rectangle { color: Theme.panel; border.color: Theme.border; radius: 4 }
        contentItem: ListView { clip: true; implicitHeight: contentHeight; model: control.popup.visible ? control.delegateModel : null; currentIndex: control.highlightedIndex; ScrollIndicator.vertical: ScrollIndicator {} }
    }
}
