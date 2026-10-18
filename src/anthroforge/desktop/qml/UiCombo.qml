import QtQuick
import QtQuick.Controls

ComboBox {
    id: control
    property string hint: ""
    implicitHeight: Theme.controlHeight; implicitWidth: 150
    font.pixelSize: 12
    leftPadding: 9; rightPadding: 24
    hoverEnabled: true
    Accessible.name: hint || displayText
    ToolTip.visible: hovered && !!hint
    ToolTip.text: hint; ToolTip.delay: 500
    contentItem: Text { text: control.displayText; color: control.enabled ? Theme.text : Theme.muted; font: control.font; verticalAlignment: Text.AlignVCenter; elide: Text.ElideRight }
    indicator: Image {
        source: "icons/chevron-down.svg"
        width: 12; height: 12; sourceSize: Qt.size(12,12)
        x: control.width-width-9; y: (control.height-height)/2
        opacity: control.enabled ? 1 : .45
    }
    background: Rectangle { radius: 4; color: Theme.field; border.color: control.activeFocus ? Theme.accent : Theme.border }
    delegate: ItemDelegate {
        required property int index
        width: ListView.view ? ListView.view.width : control.availableWidth
        height: Theme.controlHeight; leftPadding: Theme.gap; rightPadding: Theme.gap
        text: control.textAt(index)
        font.pixelSize: 12
        highlighted: control.highlightedIndex === index
        contentItem: Text { text: parent.text; font: parent.font; color: Theme.text; verticalAlignment: Text.AlignVCenter; elide: Text.ElideRight }
        background: Rectangle { radius: Theme.radius; color: parent.highlighted || parent.hovered ? Theme.hover : Theme.panel }
    }
    popup: Popup {
        y: control.height + 3; width: control.width
        implicitHeight: Math.min(contentItem.implicitHeight + 8, 330); padding: 4
        background: Rectangle { color: Theme.panel; border.color: Theme.border; radius: 4 }
        contentItem: ListView { clip: true; implicitHeight: contentHeight; model: control.popup.visible ? control.delegateModel : null; currentIndex: control.highlightedIndex; ScrollIndicator.vertical: ScrollIndicator {} }
    }
}
