import QtQuick
import QtQuick.Controls

// One numeric editor for scalar/vector/transform fields. Model values stay authoritative.
UiField {
    id: field
    property real value: 0
    property int decimals: 4
    property bool mixed: false
    property bool live: true
    property real fallbackStep: 0.01
    property real step: decimals === 0 ? 1 : Math.max(Math.pow(10,-decimals), value ? Math.pow(10,Math.floor(Math.log10(Math.abs(value)))-2) : fallbackStep)
    property real minimum: -Infinity
    property real maximum: Infinity
    property bool textEditing: false
    property bool scrubbing: false
    property real startValue: 0
    property real dragStep: 0
    property real draft: value
    signal edited(real value)
    activeFocusOnPress: false
    readOnly: !textEditing
    placeholderText: mixed ? "Mixed" : ""
    validator: RegularExpressionValidator {
        regularExpression: field.decimals === 0 ? /^[+-]?\d+$/ : /^[+-]?(?:\d+(?:[.,]\d*)?|[.,]\d+)$/
    }
    Binding { target: field; property: "text"; when: !field.textEditing && !field.scrubbing; value: field.mixed ? "" : field.value.toFixed(field.decimals) }
    function bounded(value) { return Math.max(minimum,Math.min(maximum,value)); }
    function publish(value) { if(isFinite(value) && (mixed || value !== field.value)) edited(value); }
    function beginText() { textEditing=true; forceActiveFocus(); selectAll(); }
    function commitText() {
        if(!textEditing) return;
        const parsed=Number(text.replace(",","."));
        const valid=text.trim() && acceptableInput;
        textEditing=false; focus=false;
        if(valid) publish(bounded(parsed));
    }
    function cancelEdit() {
        if(scrubbing && live) numericEdits.cancel();
        scrubbing=false; textEditing=false; focus=false;
    }
    function beginScrub() {
        if(live && !numericEdits.begin(field)) return false;
        startValue=value; draft=value; dragStep=step;
        scrubbing=true; forceActiveFocus(); return true;
    }
    function updateScrub(distance) {
        draft=bounded(Number((startValue+Math.round(distance)*dragStep).toFixed(decimals)));
        text=draft.toFixed(decimals);
        if(live) publish(draft);
    }
    function finishScrub() {
        if(!scrubbing) return;
        if(live) numericEdits.commit(field); else publish(draft);
        scrubbing=false; focus=false;
    }
    onAccepted: commitText()
    onEditingFinished: commitText()
    onEnabledChanged: if(!enabled) cancelEdit()
    Connections {
        target: numericEdits
        function onFinished(canceled) { if(field.scrubbing) { field.scrubbing=false; field.focus=false; } }
    }
    MouseArea {
        anchors.fill: parent
        enabled: !field.textEditing
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
    ToolTip.visible: hovered && !scrubbing && !textEditing
    ToolTip.text: "Drag left/right to adjust · Click to type"
}
