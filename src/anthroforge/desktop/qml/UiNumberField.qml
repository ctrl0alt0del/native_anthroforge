import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls

// One numeric editor for scalar/vector/transform fields. Model values stay authoritative.
UiField {
    id: field
    property var value: 0
    property bool exactText: false
    property var exactOffset: null
    property var propertyReference: ({})
    readonly property var propertyState: visible && propertyReference?.target ? App.shortcutPanel.propertyState(propertyReference,App.shortcutPanel.propertyQueries.versions[propertyReference.target] || 0) : ({})
    readonly property bool propertyLocked: !!propertyReference?.target && propertyState.writable === false
    property int decimals: 4
    property bool mixed: false
    property bool live: true
    property real fallbackStep: 0.01
    property real step: decimals === 0 ? 1 : Math.max(Math.pow(10,-decimals), value ? Math.pow(10,Math.floor(Math.log10(Math.abs(value)))-2) : fallbackStep)
    property real minimum: -Infinity
    property real maximum: Infinity
    property bool textEditing: false
    property bool scrubbing: false
    property var startValue: 0
    property real dragStep: 0
    property var draft: value
    signal edited(real value)
    signal exactEdited(string value)
    activeFocusOnPress: false
    readOnly: !textEditing || propertyLocked
    placeholderText: mixed ? "Mixed" : ""
    validator: RegularExpressionValidator {
        regularExpression: field.decimals === 0 ? /^[+-]?\d+$/ : /^[+-]?(?:\d+(?:[.,]\d*)?|[.,]\d+)$/
    }
    Binding { target: field; property: "text"; when: !field.textEditing && !field.scrubbing; value: field.mixed ? "" : field.formatted(field.value) }
    function formatted(value) { return exactText || value === "" ? String(value) : Number(value).toFixed(decimals); }
    function bounded(value) { return exactText ? value : Math.max(minimum,Math.min(maximum,value)); }
    function publish(value) {
        if(!isFinite(value) || (!mixed && value === field.value)) return;
        if(exactText) exactEdited(String(value)); else edited(value);
    }
    function beginText() { if(propertyLocked) return; textEditing=true; forceActiveFocus(); selectAll(); }
    function commitText() {
        if(!textEditing) return;
        const cleaned=text.trim().replace(",",".");
        const parsed=exactText ? cleaned : Number(cleaned);
        const valid=text.trim() && acceptableInput;
        textEditing=false; focus=false;
        if(valid) publish(bounded(parsed));
    }
    function cancelEdit() {
        if(scrubbing && live) App.numericEdits.cancel();
        scrubbing=false; textEditing=false; focus=false;
    }
    function beginScrub() {
        if(propertyLocked) return false;
        if(live && !App.numericEdits.begin(field)) return false;
        startValue=value; draft=value; dragStep=step;
        scrubbing=true; forceActiveFocus(); return true;
    }
    function updateScrub(distance) {
        draft=exactText ? exactOffset(startValue,Math.round(distance)) : bounded(Number((startValue+Math.round(distance)*dragStep).toFixed(decimals)));
        text=formatted(draft);
        if(live) publish(draft);
    }
    function finishScrub() {
        if(!scrubbing) return;
        if(live) App.numericEdits.commit(field); else publish(draft);
        scrubbing=false; focus=false;
    }
    onAccepted: commitText()
    onEditingFinished: commitText()
    onEnabledChanged: if(!enabled) cancelEdit()
    Connections {
        target: App.numericEdits
        function onFinished(canceled) { if(field.scrubbing) { field.scrubbing=false; field.focus=false; } }
    }
    MouseArea {
        anchors.fill: parent
        enabled: !field.textEditing && !field.propertyLocked
        acceptedButtons: Qt.LeftButton
        cursorShape: Qt.SizeHorCursor
        preventStealing: true
        property real startX: 0
        property bool moved: false
        onPressed: mouse => { startX=mouse.x; moved=false; }
        onPositionChanged: mouse => {
            if(!pressed) return;
            const distance=mouse.x-startX;
            if(!moved && Math.abs(distance)>=Qt.styleHints.startDragDistance) {
                moved=true;
                if(!field.beginScrub()) return;
            }
            if(field.scrubbing) field.updateScrub(distance);
        }
        onReleased: { if(moved) field.finishScrub(); else field.beginText(); }
        onCanceled: field.cancelEdit()
    }
    TapHandler { acceptedButtons: Qt.RightButton; enabled: !!field.propertyReference?.target; onTapped: propertyMenu.popup() }
    UiMenu {
        id: propertyMenu
        UiMenuItem { text: "Go to driving shortcut"; visible: !!field.propertyState.driver; onTriggered: App.shortcutPanel.openDriver(field.propertyReference) }
        UiMenuItem { text: field.propertyState.exposed ? "Hide shortcut" : "Expose as shortcut"; onTriggered: App.shortcutPanel.expose(field.propertyReference,"",!field.propertyState.exposed) }
    }
    ToolTip.visible: hovered && !scrubbing && !textEditing
    ToolTip.text: propertyState.reason || "Drag left/right to adjust · Click to type" + (propertyReference?.target ? " · Right-click for shortcut" : "")
}
