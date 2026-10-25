import QtQuick
import QtQuick.Controls

ComboBox {
    id: control
    property string hint: ""
    property bool enumLabels: false
    displayText: enumLabels ? DisplayNames.label(currentText) : currentText
    implicitHeight: Theme.controlHeight; implicitWidth: 150
    font.pixelSize: 12
    leftPadding: 9; rightPadding: 24
    hoverEnabled: true
    Accessible.name: hint || displayText
    ToolTip.visible: hovered && (!!hint || contentItem.truncated)
    ToolTip.text: contentItem.truncated ? displayText + (hint ? "\n" + hint : "") : hint; ToolTip.delay: 500
    FontMetrics { id: metrics; font: control.font }
    function choiceWidth() {
        let result=control.width;
        for(let i=0;i<control.count;++i) result=Math.max(result,metrics.advanceWidth(control.choiceLabel(i))+2*Theme.gap+8);
        return Math.min(result,Math.max(control.width,Overlay.overlay.width-2*Theme.gap));
    }
    function choiceLabel(index) { return enumLabels ? DisplayNames.label(textAt(index)) : textAt(index); }
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
        height: Math.max(Theme.controlHeight,implicitContentHeight+8); leftPadding: Theme.gap; rightPadding: Theme.gap
        text: control.choiceLabel(index)
        font.pixelSize: 12
        highlighted: control.highlightedIndex === index
        contentItem: Text { text: parent.text; font: parent.font; color: Theme.text; verticalAlignment: Text.AlignVCenter; wrapMode: Text.Wrap }
        background: Rectangle { radius: Theme.radius; color: parent.highlighted || parent.hovered ? Theme.hover : Theme.panel }
    }
    popup: Popup {
        objectName: "comboPopup"
        y: control.height + 3; width: control.width; margins: Theme.gap
        onAboutToShow: width=control.choiceWidth()
        implicitHeight: Math.min(contentItem.implicitHeight + 8, 330); padding: 4
        background: Rectangle { color: Theme.panel; border.color: Theme.border; radius: 4 }
        contentItem: ListView { clip: true; implicitHeight: contentHeight; model: control.popup.visible ? control.delegateModel : null; currentIndex: control.highlightedIndex; ScrollIndicator.vertical: ScrollIndicator {} }
    }
}
