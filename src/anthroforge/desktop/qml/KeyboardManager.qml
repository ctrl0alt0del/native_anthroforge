import QtQuick

// Bindings own key choices and focus policy; consumers handle semantic commands.
Item {
    id: manager
    objectName: "keyboardManager"
    required property var window
    property bool blocked: false
    property bool transforming: false
    property bool snapping: false
    property var capabilities: ({})
    function capabilityEnabled(binding) { return !binding.capability || capabilities[binding.capability] === true; }
    function commandEnabled(command) { return bindings.filter(binding=>binding.command===command).every(capabilityEnabled); }
    readonly property bool typing: !!window.activeFocusItem && window.activeFocusItem.selectByMouse !== undefined
    signal requested(string command)
    signal canceled()
    signal offsetRequested(real steps)
    signal offsetReset()
    property var pointerBindings: ({resetSurfaceOffset:Qt.MiddleButton})
    Binding { target: heldInput; property: "wheelCapture"; value: manager.snapping && !manager.blocked && !manager.typing }
    Binding { target: heldInput; property: "buttonCapture"; value: manager.snapping && !manager.blocked && !manager.typing ? manager.pointerBindings.resetSurfaceOffset : 0 }
    property var modifierBindings: ({insertPoint:Qt.ShiftModifier, snapSurface:Qt.ControlModifier,
        extendSelection:Qt.ControlModifier, precision:Qt.ShiftModifier, pan:Qt.ShiftModifier,
        deeperSelection:Qt.AltModifier, continuePlacement:Qt.ShiftModifier})
    function modifierName(action) {
        const binding=modifierBindings[action];
        return [{flag:Qt.ControlModifier,name:"Ctrl"},{flag:Qt.ShiftModifier,name:"Shift"},{flag:Qt.AltModifier,name:"Alt"}].filter(row=>(binding & row.flag)!==0).map(row=>row.name).join("+");
    }
    readonly property int modifiers: blocked || typing ? 0 : heldInput.modifiers
    readonly property var modifierPrefixes: ["", "Shift+", "Ctrl+", "Alt+", "Ctrl+Shift+", "Ctrl+Alt+", "Alt+Shift+", "Ctrl+Alt+Shift+"]
    function held(action) { return matches(action, modifiers); }
    function shortcut(command) { return bindings.find(binding => binding.command===command)?.key || ""; }
    function matches(action, mask) {
        const binding=modifierBindings[action];
        return !blocked && !typing && binding !== undefined && (mask & binding) === binding;
    }
    function sequences(binding) {
        if(!binding.allowModifiers) return [binding.key];
        const parts=binding.key.split("+"); const key=parts.pop();
        const excluded=binding.excludeModifiers || [];
        return modifierPrefixes.filter(prefix=>parts.every(part=>prefix.includes(part+"+")) && !excluded.some(part=>prefix.includes(part+"+"))).map(prefix=>prefix+key);
    }
    onBlockedChanged: { if(blocked) heldInput.clear(); }
    onTypingChanged: { if(typing) heldInput.clear(); }
    Connections {
        target: heldInput
        function onCanceled() { manager.canceled(); }
        function onWheelTurned(steps) { manager.offsetRequested(steps); }
        function onButtonTriggered() { manager.offsetReset(); }
    }
    property var bindings: [
        {command:"new", key:StandardKey.New, scope:"document"},
        {command:"open", key:StandardKey.Open, scope:"document"},
        {command:"save", key:StandardKey.Save, scope:"document"},
        {command:"saveAs", key:StandardKey.SaveAs, scope:"document"},
        {command:"importMesh", key:"Ctrl+I", scope:"document"},
        {command:"undo", key:StandardKey.Undo}, {command:"redo", key:StandardKey.Redo},
        {command:"deleteSelection", key:"Delete"}, {command:"frame", key:"F"},
        {command:"move", key:"W", capability:"transform"}, {command:"rotate", key:"E", capability:"transform"},
        {command:"grab", key:"G", duringTransform:true, capability:"transform"}, {command:"turn", key:"R", duringTransform:true, capability:"transform"},
        {command:"resize", key:"S", duringTransform:true, capability:"transform"},
        {command:"viewX", key:"1", duringTransform:true, allowModifiers:true},
        {command:"viewY", key:"2", duringTransform:true, allowModifiers:true},
        {command:"viewZ", key:"3", duringTransform:true, allowModifiers:true},
        {command:"restoreView", key:"4", duringTransform:true, allowModifiers:true},
        {command:"reportFeedback", key:"F12", duringTransform:true, allowModifiers:true, excludeModifiers:["Shift"], allowTyping:true, allowBlocked:true},
        {command:"recordPerformance", key:"Shift+F12", duringTransform:true, allowModifiers:true, allowTyping:true},
        {command:"confirm", key:"Return", duringTransform:true, allowModifiers:true},
        {command:"confirm", key:"Enter", duringTransform:true, allowModifiers:true},
        {command:"removeLastPoint", key:"Backspace", duringTransform:true},
        {command:"projection", key:"5"}, {command:"xray", key:"Alt+Z"},
        {command:"cancel", key:"Escape", allowModifiers:true, duringTransform:true}
    ]
    Instantiator {
        model: manager.bindings
        delegate: Shortcut {
            required property var modelData
            sequences: manager.sequences(modelData)
            context: modelData.allowBlocked ? Qt.ApplicationShortcut : Qt.WindowShortcut
            autoRepeat: false
            enabled: manager.capabilityEnabled(modelData) && (!manager.blocked || !!modelData.allowBlocked) && (!manager.typing || modelData.scope === "document" || !!modelData.allowTyping) && (!manager.transforming || !!modelData.duringTransform)
            onActivated: manager.requested(modelData.command)
        }
    }
}
