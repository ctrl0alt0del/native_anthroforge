import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

ApplicationWindow {
    id: window
    width: 1440; height: 900; minimumWidth: 1050; minimumHeight: 680
    visible: true
    title: "AnthroForge — " + workspace.documentName + (workspace.state.dirty ? " *" : "")
    color: Theme.background
    font.family: "Segoe UI"; font.pixelSize: 12
    palette.window: Theme.panel; palette.windowText: Theme.text; palette.text: Theme.text
    palette.buttonText: Theme.text; palette.button: Theme.header; palette.base: Theme.field
    palette.highlight: Theme.selection; palette.highlightedText: Theme.text
    property string chosenImport: ""
    property string blockedSavePath: ""
    property string replacementPath: ""
    property bool closingConfirmed: false
    property bool activityOpen: false
    property bool issuesOpen: false
    property string activeTool: "Move"
    readonly property bool typing: keyboard.typing
    readonly property bool modalOpen: reportDialog.visible || workspaceManager.visible || importOptions.visible || saveChoice.visible || waitingDialog.visible || discardDialog.visible || closeDialog.visible || focusDialog.visible || helpDialog.visible || messageDialog.visible || inspector.dialogVisible || deleteDialog.visible || importFile.visible || openDialog.visible || saveDialog.visible
    readonly property int activeJobCount: workspace.activityModel.activeCount
    readonly property bool jobFailed: workspace.activityModel.hasFailures
    function inspectScene(): string { return viewport.inspectScene(); }
    function saveProject() {
        viewport.forceActiveFocus();
        if (workspace.state.path) workspace.saveProject(workspace.state.path, "");
        else saveDialog.open();
    }
    onClosing: function(close) {
        if (workspace.state.dirty && !closingConfirmed) { close.accepted = false; closeDialog.open(); }
    }
    Action { id: newAction; text: "New project"; enabled: !window.modalOpen; onTriggered: { viewport.forceActiveFocus(); workspace.newDocument(); } }
    Action { id: openAction; text: "Open project…"; enabled: !window.modalOpen; onTriggered: { viewport.forceActiveFocus(); openDialog.open(); } }
    Action { id: saveAction; text: "Save"; enabled: !window.modalOpen; onTriggered: window.saveProject() }
    Action { id: saveAsAction; text: "Save as…"; enabled: !window.modalOpen; onTriggered: { viewport.forceActiveFocus(); saveDialog.open(); } }
    Action { id: importAction; text: "Import mesh…"; enabled: !window.modalOpen; onTriggered: importFile.open() }
    Action { id: undoAction; text: "Undo"; enabled: !window.modalOpen && !window.typing; onTriggered: workspace.run("undo",{}) }
    Action { id: redoAction; text: "Redo"; enabled: !window.modalOpen && !window.typing; onTriggered: workspace.run("redo",{}) }
    header: ColumnLayout {
        spacing: 0
        Rectangle {
            Layout.fillWidth: true; implicitHeight: 35; color: "#25262a"
            RowLayout {
                anchors.fill: parent; anchors.leftMargin: 12; anchors.rightMargin: 10; spacing: 10
                Label { text: "ANTHROFORGE"; font.bold: true; font.pixelSize: 12; font.letterSpacing: 1; color: Theme.text }
                Label { text: "0.1.7"; color: Theme.accent; font.pixelSize: 10 }
                MenuBar {
                    background: Item {}
                    Menu { title: "File"; MenuItem { action: newAction } MenuItem { action: openAction } MenuSeparator {} MenuItem { action: saveAction } MenuItem { action: saveAsAction } MenuSeparator {} MenuItem { action: importAction } MenuSeparator {} MenuItem { objectName: "exportInspectionMenu"; text: "Export inspection report…"; enabled: !workspace.inspectionExport.state.busy && !workspace.state.editing; onTriggered: { viewport.storeCamera(); reportDialog.open(); } } }
                    Menu { title: "Edit"; MenuItem { action: undoAction } MenuItem { action: redoAction } MenuSeparator {} MenuItem { text: "Delete selected…    Delete"; enabled: !!workspace.selectedId && !workspace.selectedData.readonly; onTriggered: deleteDialog.request(workspace.selectedId) } }
                    Menu {
                        title: "View"
                        MenuItem { text: "Frame selected    F"; onTriggered: workspace.frameSelection() }
                        MenuItem { objectName: "restoreViewMenu"; text: "Restore view    "+keyboard.shortcut("restoreView"); enabled: viewport.canRestoreView; onTriggered: viewport.restoreView() }
                        MenuItem { text: "Orthographic"; checkable: true; checked: viewport.orthographic; onTriggered: viewport.orthographic = checked }
                        MenuItem { text: "X-ray    Alt+Z"; checkable: true; checked: viewport.xray; onTriggered: viewport.xray = checked }
                        MenuSeparator {}
                        MenuItem { text: "Transform handles"; checkable: true; checked: workspace.state.handles; onTriggered: workspace.run("workspace.update",{handles:checked}) }
                        MenuItem { text: "Attachment markers"; checkable: true; checked: workspace.state.anchors; onTriggered: workspace.run("workspace.update",{anchors:checked}) }
                        MenuItem { text: "Performance diagnostics"; checkable: true; checked: workspace.state.diagnostics; onTriggered: workspace.run("workspace.update",{diagnostics:checked}) }
                        MenuItem { text: "Activity panel"; checkable: true; checked: window.activityOpen; onTriggered: window.activityOpen = checked }
                        MenuItem { text: "Issues panel"; checkable: true; checked: window.issuesOpen; onTriggered: { window.issuesOpen = checked; if(checked) window.activityOpen = false; } }
                        MenuSeparator {}
                        MenuItem { text: (performance.state.recording ? "Stop recording" : "Record performance") + "    " + keyboard.shortcut("recordPerformance"); onTriggered: performance.toggle() }
                    }
                    Menu { title: "Help"; MenuItem { text: "Navigation and shortcuts"; onTriggered: helpDialog.open() } }
                }
                Item { Layout.fillWidth: true }
                ProfileStatus { }
                Label { text: "Workspace"; color: Theme.muted; font.pixelSize: 11 }
                UiCombo { Layout.preferredWidth: 175; model: workspace.state.workspaces; currentIndex: workspace.state.workspace; onActivated: workspace.run("workspace.select",{index:currentIndex}) }
                UiButton { objectName: "manageWorkspace"; text: "Manage…"; enabled: !workspace.state.waiting && !workspace.state.editing; onClicked: workspaceManager.open() }
                UiButton { text: "Focus…"; hint: "Create a workspace from the selected SCP"; enabled: !!workspace.selectedId && !workspace.state.waiting; onClicked: focusDialog.open() }
            }
        }
        Rectangle {
            Layout.fillWidth: true; implicitHeight: 42; color: Theme.panel
            RowLayout {
                anchors.fill: parent; anchors.leftMargin: 10; anchors.rightMargin: 10; spacing: 6
                UiButton { objectName: "createPrimitive"; text: "Create Primitive"; glyph: "plus"; primary: true; enabled: !workspace.state.waiting; onClicked: createMenu.popup() }
                UiButton { action: importAction; glyph: "import"; hint: "Import an OBJ, STL or PLY mesh (Ctrl+I)" }
                UiButton { action: saveAction; glyph: "save"; hint: "Save project (Ctrl+S)" }
                Rectangle { Layout.leftMargin: 6; Layout.rightMargin: 6; implicitWidth: 1; implicitHeight: 20; color: Theme.border }
                UiButton { glyph: "undo"; hint: "Undo (Ctrl+Z)"; enabled: undoAction.enabled; onClicked: undoAction.trigger() }
                UiButton { glyph: "redo"; hint: "Redo (Ctrl+Y)"; enabled: redoAction.enabled; onClicked: redoAction.trigger() }
                Item { Layout.fillWidth: true }
                UiCheck { text: "Attachments"; checked: workspace.state.attachments; enabled: !workspace.state.waiting; onClicked: workspace.run("attachments.enable",{enabled:checked}) }
                Rectangle { implicitWidth: 1; implicitHeight: 20; color: Theme.border; Layout.leftMargin: 8; Layout.rightMargin: 8 }
                Label { text: "Update"; color: Theme.muted }
                UiCombo { implicitWidth: 112; model: ["Live","On release","Manual"]; currentIndex: Math.max(0,["LIVE","ON_RELEASE","MANUAL"].indexOf(workspace.state.mode)); hint: "When dependent geometry is recalculated"; onActivated: workspace.run("update_mode",{mode:["LIVE","ON_RELEASE","MANUAL"][currentIndex]}) }
                UiButton { text: "Recalculate"; hint: "Update pending dependent geometry"; enabled: !workspace.state.waiting; onClicked: workspace.run("evaluate",{}) }
            }
        }
    }
    SplitView {
        id: panels; anchors.fill: parent; orientation: Qt.Horizontal
        handle: Rectangle { implicitWidth: 4; color: SplitHandle.hovered || SplitHandle.pressed ? Theme.accent : "#1b1c1f" }
        Rectangle {
            SplitView.preferredWidth: 240; SplitView.minimumWidth: 195; SplitView.maximumWidth: 440
            color: Theme.panel
            Outliner { anchors.fill: parent; anchors.margins: 10; onImportRequested: importFile.open(); onDeleteRequested: entity => deleteDialog.request(entity) }
        }
        ColumnLayout {
            SplitView.fillWidth: true; SplitView.minimumWidth: 300; spacing: 0
            Rectangle {
                Layout.fillWidth: true; implicitHeight: 33; color: Theme.header
                RowLayout {
                    anchors.fill: parent; anchors.leftMargin: 10; anchors.rightMargin: 6; spacing: 6
                    Label { text: "3D VIEWPORT"; color: Theme.muted; font.pixelSize: 10; font.letterSpacing: 1; Layout.fillWidth: true }
                    UiButton { text: viewport.orthographic ? "Orthographic" : "Perspective"; flatStyle: true; hint: "Toggle perspective / orthographic projection (5)"; onClicked: viewport.orthographic = !viewport.orthographic }
                    UiButton { glyph: "frame"; flatStyle: true; hint: "Frame selected (F)"; onClicked: workspace.frameSelection() }
                    UiButton { text: "Overlays"; flatStyle: true; onClicked: overlays.open() }
                }
            }
            Item {
                Layout.fillWidth: true; Layout.fillHeight: true
                Viewport { id: viewport; objectName: "viewport"; anchors.fill: parent; toolMode: window.activeTool; keyboard: keyboard; onImportRequested: importFile.open() }
                Column {
                    anchors.left: parent.left; anchors.top: parent.top; anchors.margins: 10; spacing: 5
                    Repeater {
                        model: [{name:"Move",icon:"move",command:"grab"},{name:"Rotate",icon:"rotate",command:"turn"},{name:"Scale",icon:"scale",command:"resize"}]
                        UiButton { required property var modelData; objectName: "tool"+modelData.name; width: 34; height: 34; glyph: modelData.icon; checkable: true; checked: window.activeTool === modelData.name; hint: modelData.name+" gizmo · "+keyboard.shortcut(modelData.command)+": mouse transform"; onClicked: window.activeTool = modelData.name }
                    }
                }
            }
            Rectangle {
                Layout.fillWidth: true; implicitHeight: 30; color: Theme.header
                RowLayout {
                    anchors.fill: parent; anchors.leftMargin: 7; anchors.rightMargin: 8
                    UiButton { objectName: "activityToggle"; flatStyle: true; text: (window.activityOpen ? "▾" : "▸") + "  Activity"; onClicked: { window.activityOpen = !window.activityOpen; if(window.activityOpen) window.issuesOpen = false; } }
                    UiButton { objectName: "issuesToggle"; flatStyle: true; text: (window.issuesOpen ? "▾" : "▸") + "  Issues ("+(workspace.issuePanel.state.count || 0)+")"; hint: workspace.issuePanel.state.summary || "Issue reporting"; onClicked: { window.issuesOpen = !window.issuesOpen; if(window.issuesOpen) window.activityOpen = false; } }
                    Label { text: window.activeJobCount ? window.activeJobCount + " jobs in progress" : window.jobFailed ? "A calculation failed · open Activity" : "Up to date"; color: window.jobFailed ? Theme.danger : window.activeJobCount ? Theme.accent : Theme.muted; font.pixelSize: 11; Layout.fillWidth: true; elide: Text.ElideRight }
                    Label { text: workspace.treeRows.length + " objects · "+workspace.state.display_units; color: Theme.muted; font.pixelSize: 11 }
                }
            }
            Rectangle { Layout.fillWidth: true; implicitHeight: window.activityOpen ? 160 : 0; visible: window.activityOpen; color: Theme.panel; Activity { anchors.fill: parent; anchors.margins: 10 } }
            Rectangle { Layout.fillWidth: true; implicitHeight: window.issuesOpen ? 290 : 0; visible: window.issuesOpen; color: Theme.panel; Issues { anchors.fill: parent; anchors.margins: 10 } }
        }
        Rectangle {
            SplitView.preferredWidth: 310; SplitView.minimumWidth: 280; SplitView.maximumWidth: 500
            color: Theme.panel
            ColumnLayout {
                anchors.fill: parent; spacing: 0
                Rectangle { Layout.fillWidth: true; implicitHeight: 33; color: Theme.header; Label { anchors.verticalCenter: parent.verticalCenter; x: 12; text: "PROPERTIES"; color: Theme.muted; font.pixelSize: 10; font.letterSpacing: 1 } }
                Inspector { id: inspector; objectName: "inspector"; Layout.fillWidth: true; Layout.fillHeight: true; Layout.margins: 10; onPickAnchor: function(mode) { viewport.anchorMode = mode; }; onDeleteRequested: entity => deleteDialog.request(entity) }
            }
        }
    }
    footer: Rectangle {
        color: "#25262a"; implicitHeight: 25
        RowLayout {
            anchors.fill: parent; anchors.leftMargin: 10; anchors.rightMargin: 10; spacing: 12
            Rectangle { implicitWidth: 6; implicitHeight: 6; radius: 3; color: workspace.state.blocked ? Theme.accent : Theme.success }
            Label { text: workspace.state.message || "Middle/right drag: orbit   ·   Shift-drag: pan   ·   Wheel: zoom"; color: Theme.muted; font.pixelSize: 11; elide: Text.ElideRight; Layout.fillWidth: true }
            UiButton { visible: !!workspace.state.message; flatStyle: true; text: "Details"; implicitHeight: 22; onClicked: messageDialog.open() }
            UiButton { text: "Report folder"; visible: !!workspace.inspectionExport.state.path && !workspace.inspectionExport.state.busy; implicitHeight: 22; onClicked: workspace.inspectionExport.showFolder() }
            Label { text: "Rev " + workspace.state.revision + (workspace.state.dirty ? " · Unsaved" : " · Saved"); color: workspace.state.dirty ? Theme.accent : Theme.muted; font.pixelSize: 11 }
        }
    }
    Menu {
        id: createMenu
        MenuItem { text: "Ordered curve loft"; onTriggered: authoring.create("LOFT","CAPSULE") }
        MenuSeparator {}
        MenuItem { text: "Curve-deformed box"; onTriggered: authoring.create("BODY","BOX") }
        MenuItem { text: "Curve-deformed cylinder"; onTriggered: authoring.create("BODY","CYLINDER") }
        MenuItem { text: "Curve-deformed capsule"; onTriggered: authoring.create("BODY","CAPSULE") }
        MenuSeparator {}
        MenuItem { text: "Import mesh…"; onTriggered: importFile.open() }
    }
    FileDialog { id: reportDialog; title: "Export inspection report"; fileMode: FileDialog.SaveFile; defaultSuffix: "afinspection.zip"; nameFilters: ["Inspection report (*.afinspection.zip)"]; onAccepted: workspace.inspectionExport.start(selectedFile.toString()) }
    WorkspaceManager { id: workspaceManager; anchors.centerIn: parent }
    Popup {
        id: overlays; x: Math.max(0,window.width-650); y: 110; padding: 14
        background: Rectangle { color: Theme.panel; border.color: Theme.border; radius: 6 }
        ColumnLayout {
            Label { text: "VIEWPORT OVERLAYS"; color: Theme.muted; font.pixelSize: 10 }
            UiCheck { text: "Transform handles"; checked: workspace.state.handles; onClicked: workspace.run("workspace.update",{handles:checked}) }
            UiCheck { text: "Attachment markers"; checked: workspace.state.anchors; onClicked: workspace.run("workspace.update",{anchors:checked}) }
            UiCheck { text: "Performance diagnostics"; checked: workspace.state.diagnostics; onClicked: workspace.run("workspace.update",{diagnostics:checked}) }
        }
    }
    Dialog {
        id: helpDialog; title: "Navigation and shortcuts"; modal: true; anchors.centerIn: parent; standardButtons: Dialog.Close
        Label { text: "G / R / S    Start Move / Rotate / Scale\nLeft click / Enter    Confirm transform\nRight click / Escape    Cancel transform\nW / E    Select Move / Rotate gizmo\nF    Frame selected\n1 / 2 / 3    X / Y / Z view, centered with zoom preserved\n"+keyboard.shortcut("restoreView")+"    Restore camera before axis views\n5    Perspective / Orthographic\nAlt+Z    X-ray\nAlt-click    Select through overlapping objects\nMiddle or right drag    Orbit\nShift + drag    Pan\nMouse wheel    Zoom\nEscape    Cancel transform or anchor picking\nCtrl+I    Import mesh\nDelete    Remove selected object, preserving children\nShift while transforming    Fine adjustment\nShift in curve editing    Preview; click to insert points\nCtrl while moving a curve point    Snap to another SCP\nWheel while snapping    Surface offset\nMiddle click / release Ctrl    Reset offset\nCtrl-click a component    Extend selection"; lineHeight: 1.7; color: Theme.text }
    }
    Dialog { id: messageDialog; title: "Last operation"; modal: true; anchors.centerIn: parent; width: Math.min(560, window.width-80); standardButtons: Dialog.Close; Label { width: parent.width; text: workspace.state.message; wrapMode: Text.WrapAnywhere; color: Theme.text } }
    FileDialog { id: importFile; title: "Import primitive mesh"; nameFilters: ["Mesh files (*.obj *.stl *.ply)"]; onAccepted: { window.chosenImport = selectedFile.toString(); importUnits.currentIndex = 0; importOptions.open(); } }
    FileDialog { id: openDialog; title: "Open AnthroForge project"; nameFilters: ["AnthroForge project (*.anthroforge)"]; onAccepted: workspace.requestDocument(selectedFile.toString()) }
    FileDialog { id: saveDialog; title: "Save AnthroForge project"; fileMode: FileDialog.SaveFile; defaultSuffix: "anthroforge"; nameFilters: ["AnthroForge project (*.anthroforge)"]; onAccepted: workspace.saveProject(selectedFile.toString(),""); onRejected: workspace.cancelSaveWait() }
    Dialog {
        id: importOptions; title: "Import primitive"; modal: true; anchors.centerIn: parent; width: 420
        ColumnLayout {
            anchors.fill: parent
            Label { text: window.chosenImport; Layout.fillWidth: true; wrapMode: Text.WrapAnywhere; color: Theme.muted }
            Label { text: "Source units (required)" }
            UiCombo { id: importUnits; Layout.fillWidth: true; model: ["Choose source units…","Metres","Centimetres","Millimetres"] }
            Label { text: "Parent SCP"; visible: workspace.treeRows.length > 0 }
            UiCombo { id: importParent; visible: workspace.treeRows.length > 0; Layout.fillWidth: true; model: workspace.treeRows.filter(row => !row.is_control); textRole: "name"; valueRole: "id"; currentIndex: Math.max(0,indexOfValue(workspace.selectedId)) }
            UiCheck { id: sourceYUp; text: "Convert Y-up source to Z-up" }
            Label { text: "One SCP per file. Geometry only; materials and textures are ignored."; Layout.fillWidth: true; wrapMode: Text.WordWrap; color: Theme.muted }
            RowLayout {
                Item { Layout.fillWidth: true }
                UiButton { text: "Cancel"; onClicked: importOptions.close() }
                UiButton {
                    text: "Import"; enabled: importUnits.currentIndex > 0
                    onClicked: { workspace.importMesh(window.chosenImport,[0,1,.01,.001][importUnits.currentIndex],workspace.treeRows.length ? importParent.currentValue : "",sourceYUp.checked); importOptions.close(); }
                }
            }
        }
    }
    Dialog {
        id: focusDialog; title: "Create focused workspace"; modal: true; anchors.centerIn: parent
        standardButtons: Dialog.Ok | Dialog.Cancel
        ColumnLayout {
            UiField { id: focusName; placeholderText: "Workspace name"; text: workspace.selectedData.name || "Focused workspace" }
            UiCheck { id: includeChildren; text: "Include descendants"; checked: true }
            Label { text: "Other SCPs remain transparent and read-only."; color: Theme.muted }
        }
        onAccepted: workspace.run("workspace.create",{name:focusName.text,members:[workspace.selectedId],children:includeChildren.checked})
    }
    Dialog {
        id: saveChoice; title: "Calculations are still running"; modal: true; anchors.centerIn: parent; closePolicy: Popup.NoAutoClose
        ColumnLayout {
            Label { text: "Choose the document revision to save." }
            UiButton { text: "Wait for queued calculations, then save"; Layout.fillWidth: true; onClicked: { saveChoice.close(); workspace.saveProject(window.blockedSavePath,"wait"); } }
            UiButton { text: "Save latest committed revision"; Layout.fillWidth: true; onClicked: { saveChoice.close(); workspace.saveProject(window.blockedSavePath,"checkpoint"); } }
            UiButton { text: "Cancel save"; Layout.fillWidth: true; onClicked: { saveChoice.close(); workspace.cancelSaveWait(); } }
        }
    }
    Dialog {
        id: waitingDialog; title: "Finishing project operation"; modal: true; anchors.centerIn: parent; closePolicy: Popup.NoAutoClose
        visible: workspace.state.waiting
        ColumnLayout {
            BusyIndicator { running: true; Layout.alignment: Qt.AlignHCenter }
            Label { text: "Waiting for calculations or file preparation to finish.\nYou can switch to another application while AnthroForge works." }
            UiButton { text: "Cancel waiting"; onClicked: workspace.cancelSaveWait() }
        }
    }
    Dialog {
        id: discardDialog; title: "Unsaved changes"; modal: true; anchors.centerIn: parent
        ColumnLayout {
            Label { text: "Save the current project before replacing it, or discard its changes."; width: 330; wrapMode: Text.WordWrap }
            UiButton { text: "Save and continue"; Layout.fillWidth: true; onClicked: { discardDialog.close(); workspace.afterSave(window.replacementPath); window.saveProject(); } }
            UiButton { text: "Discard and continue"; Layout.fillWidth: true; onClicked: { discardDialog.close(); workspace.replaceDocument(window.replacementPath); } }
            UiButton { text: "Cancel"; Layout.fillWidth: true; onClicked: discardDialog.close() }
        }
    }
    Dialog {
        id: closeDialog; title: "Close with unsaved changes?"; modal: true; anchors.centerIn: parent
        standardButtons: Dialog.Save | Dialog.Discard | Dialog.Cancel
        Label { text: "Save your project to keep these changes." }
        onAccepted: { workspace.afterSave("@close"); window.saveProject(); }
        onDiscarded: { window.closingConfirmed = true; window.close(); }
    }
    Connections {
        target: workspace
        function onSaveChoiceRequested(path) { window.blockedSavePath = path; saveChoice.open(); }
        function onDiscardRequested(path) { window.replacementPath = path; discardDialog.open(); }
        function onCloseReady() { window.closingConfirmed = true; window.close(); }
    }
    DeleteDialog { id: deleteDialog }
    KeyboardManager {
        id: keyboard; window: window; blocked: window.modalOpen || workspace.state.waiting; transforming: viewport.transforming; snapping: viewport.snapping
        onRequested: command => window.dispatchShortcut(command)
        onCanceled: viewport.cancelTransform()
        onOffsetRequested: steps => viewport.surfaceOffset(steps)
        onOffsetReset: viewport.resetSurfaceOffset()
    }
    readonly property var shortcutCommands: ({
        new: () => newAction.trigger(), open: () => openAction.trigger(), save: () => saveAction.trigger(),
        saveAs: () => saveAsAction.trigger(), importMesh: () => importAction.trigger(),
        undo: () => undoAction.trigger(), redo: () => redoAction.trigger(),
        deleteSelection: () => deleteDialog.request(workspace.selectedId), frame: () => workspace.frameSelection(),
        move: () => activeTool = "Move", rotate: () => activeTool = "Rotate", scale: () => activeTool = "Scale",
        grab: () => viewport.startModalTransform("Move"), turn: () => viewport.startModalTransform("Rotate"), resize: () => viewport.startModalTransform("Scale"),
        viewX: () => viewport.setView("Right"), viewY: () => viewport.setView("Front"), viewZ: () => viewport.setView("Top"),
        restoreView: () => viewport.restoreView(),
        recordPerformance: () => performance.toggle(),
        confirm: () => viewport.confirmTransform(),
        projection: () => viewport.orthographic = !viewport.orthographic, xray: () => viewport.xray = !viewport.xray,
        cancel: () => { workspace.inspectionTools.cancel(); viewport.cancelTransform(); viewport.anchorMode = ""; viewport.forceActiveFocus(); }
    })
    function dispatchShortcut(command) {
        const action = shortcutCommands[command];
        if (action) action();
    }
}
