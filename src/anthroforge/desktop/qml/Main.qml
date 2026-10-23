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
    palette.light: Theme.hover; palette.midlight: Theme.selection; palette.mid: Theme.hover
    palette.dark: Theme.border; palette.alternateBase: Theme.header; palette.toolTipBase: Theme.header
    palette.toolTipText: Theme.text; palette.placeholderText: Theme.muted
    palette.disabled.windowText: Theme.muted; palette.disabled.buttonText: Theme.muted
    property string chosenImport: ""
    property string blockedSavePath: ""
    property string replacementPath: ""
    property bool closingConfirmed: false
    property bool activityOpen: false
    property bool issuesOpen: false
    Connections { target: workspace.tissueInspection; function onFindingsRequested() { window.issuesOpen=true; window.activityOpen=false; } }
    property string activeTool: "Move"
    readonly property var keyboardManager: keyboard
    readonly property bool typing: keyboard.typing
    readonly property bool modalOpen: preferencesDialog.visible || surfaceGrouping.visible || reportsDialog.visible || feedbackDialog.visible || imageFile.visible || reportDialog.visible || importOptions.visible || saveChoice.visible || waitingDialog.visible || discardDialog.visible || closeDialog.visible || helpDialog.visible || messageDialog.visible || inspector.dialogVisible || deleteDialog.visible || importFile.visible || openDialog.visible || saveDialog.visible
    readonly property int activeJobCount: workspace.activityModel.activeCount
    readonly property bool jobFailed: workspace.activityModel.hasFailures
    function inspectScene(): string { return viewport.inspectScene(); }
    function saveProject() {
        viewport.forceActiveFocus();
        if (workspace.state.path) workspace.saveProject(workspace.state.path, "");
        else saveDialog.open();
    }
    onClosing: function(close) {
        if (feedback.state.busy || reportBrowser.state.busy || reportsDialog.editingDescription) { close.accepted=false; return; }
        if (workspace.state.dirty && !closingConfirmed) { close.accepted = false; closeDialog.open(); }
    }
    Action { id: newAction; text: "New project"; enabled: !window.modalOpen; onTriggered: { viewport.forceActiveFocus(); workspace.newDocument(); } }
    Action { id: openAction; text: "Open project…"; enabled: !window.modalOpen; onTriggered: { viewport.forceActiveFocus(); openDialog.open(); } }
    Action { id: saveAction; text: "Save"; enabled: !window.modalOpen; onTriggered: window.saveProject() }
    Action { id: saveAsAction; text: "Save as…"; enabled: !window.modalOpen; onTriggered: { viewport.forceActiveFocus(); saveDialog.open(); } }
    Action { id: importAction; text: "Import mesh…"; enabled: !window.modalOpen; onTriggered: importFile.open() }
    Action { id: undoAction; text: "Undo"; enabled: !window.modalOpen && !window.typing; onTriggered: workspace.run("undo",{}) }
    Action { id: redoAction; text: "Redo"; enabled: !window.modalOpen && !window.typing; onTriggered: workspace.run("redo",{}) }
    Action { id: tissueAction; text: "Create Tissue"; enabled: !window.modalOpen && !workspace.state.waiting && !workspace.selectedData.readonly && !!workspace.selectedData.tissue_presets?.length; onTriggered: workspace.createConstruction("tissue.create",{source:workspace.selectedData.id}) }
    header: ColumnLayout {
        spacing: 0
        Rectangle {
            Layout.fillWidth: true; implicitHeight: 40; color: "#25262a"
            RowLayout {
                anchors.fill: parent; anchors.leftMargin: 12; anchors.rightMargin: 10; spacing: 10
                Label { text: "ANTHROFORGE"; font.bold: true; font.pixelSize: 12; font.letterSpacing: 1; color: Theme.text }
                Label { objectName: "applicationVersion"; text: Application.version; color: Theme.accent; font.pixelSize: 10 }
                UiMenuBar {
                    background: Item {}
                    UiMenu { title: "File"; UiMenuItem { action: newAction } UiMenuItem { action: openAction } MenuSeparator {} UiMenuItem { action: saveAction } UiMenuItem { action: saveAsAction } MenuSeparator {} UiMenuItem { action: importAction } MenuSeparator {} UiMenuItem { objectName: "exportInspectionMenu"; text: "Export inspection report…"; enabled: !workspace.inspectionExport.state.busy && !workspace.state.editing; onTriggered: { viewport.storeCamera(); reportDialog.open(); } } }
                    UiMenu {
                        title: "Edit"
                        UiMenuItem { action: undoAction }
                        UiMenuItem { action: redoAction }
                        MenuSeparator {}
                        UiMenuItem { text: "Delete selected"; shortcutHint: keyboard.shortcut("deleteSelection"); enabled: !!workspace.selectedId && !workspace.selectedData.readonly; onTriggered: deleteDialog.request(workspace.selectedId) }
                        MenuSeparator {}
                        UiMenuItem { objectName: "preferencesMenu"; text: "Preferences…"; enabled: !window.modalOpen && !workspace.state.editing; onTriggered: preferencesDialog.open() }
                    }
                    UiMenu { title: "Create"; UiMenuItem { action: tissueAction } }
                    UiMenu {
                        title: "View"
                        UiMenuItem { text: "Frame selected"; shortcutHint: "F"; onTriggered: workspace.frameSelection() }
                        UiMenuItem { objectName: "restoreViewMenu"; text: "Restore view"; shortcutHint: keyboard.shortcut("restoreView"); enabled: viewport.canRestoreView; onTriggered: viewport.restoreView() }
                        UiMenuItem { text: "Orthographic"; checkable: true; checked: viewport.orthographic; onTriggered: viewport.orthographic = checked }
                        UiMenuItem { text: "X-ray"; shortcutHint: "Alt+Z"; checkable: true; checked: viewport.xray; onTriggered: viewport.xray = checked }
                        MenuSeparator {}
                        UiMenuItem { text: "Transform handles"; checkable: true; checked: workspace.state.handles; onTriggered: workspace.run("workspace.update",{handles:checked}) }
                        UiMenuItem { text: "Attachment markers"; checkable: true; checked: workspace.state.anchors; onTriggered: workspace.run("workspace.update",{anchors:checked}) }
                        UiMenuItem { text: "Performance diagnostics"; checkable: true; checked: workspace.state.diagnostics; onTriggered: workspace.run("workspace.update",{diagnostics:checked}) }
                        UiMenuItem { text: "Activity panel"; checkable: true; checked: window.activityOpen; onTriggered: window.activityOpen = checked }
                        UiMenuItem { text: "Issues panel"; checkable: true; checked: window.issuesOpen; onTriggered: { window.issuesOpen = checked; if(checked) window.activityOpen = false; } }
                        MenuSeparator {}
                        UiMenuItem { text: performance.state.recording ? "Stop recording" : "Record performance"; shortcutHint: keyboard.shortcut("recordPerformance"); onTriggered: performance.toggle() }
                    }
                    UiMenu {
                        title: "Help"; objectName: "helpMenu"
                        UiMenuItem { objectName: "reportFeedbackMenu"; text: "Report a bug / recommendation…"; shortcutHint: keyboard.shortcut("reportFeedback"); enabled: !window.modalOpen && !feedback.state.active; onTriggered: feedback.request(window) }
                        UiMenuItem { objectName: "viewReportsMenu"; text: "View reports…"; enabled: !window.modalOpen; onTriggered: reportsDialog.open() }
                        UiMenuItem { text: "Navigation and shortcuts"; onTriggered: helpDialog.open() }
                    }
                }
                Item { Layout.fillWidth: true }
                ProfileStatus { keyboard: window.keyboardManager }
                Label { text: "Workspace"; color: Theme.muted; font.pixelSize: 11 }
                WorkspaceSelector { Layout.preferredWidth: 175 }
                UiButton { objectName: "manageWorkspace"; text: "Manage…"; enabled: !workspace.state.waiting && !workspace.state.editing; onClicked: workspaceManager.open() }
                UiButton { objectName: "focusSelection"; text: "Focus"; hint: "Focus selected anatomy and descendants"; enabled: !!workspace.selectedId && !workspace.selectedData.is_construction && !workspace.selectedData.is_control && !workspace.state.waiting; onClicked: workspace.focusSelection() }
            }
        }
        Rectangle {
            Layout.fillWidth: true; implicitHeight: 42; color: Theme.panel
            RowLayout {
                anchors.fill: parent; anchors.leftMargin: 10; anchors.rightMargin: 10; spacing: 6
                UiButton { objectName: "createPrimitive"; text: "Create Primitive"; glyph: "plus"; primary: true; enabled: !workspace.state.waiting; onClicked: createMenu.popup() }
                UiButton { objectName: "createTissueToolbar"; action: tissueAction; glyph: "plus" }
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
            ObjectBrowser {
                anchors.fill: parent; anchors.margins: Theme.inset; keyboard: window.keyboardManager
                onImportRequested: importFile.open(); onDeleteRequested: entity => deleteDialog.request(entity)
            }
        }
        ColumnLayout {
            SplitView.fillWidth: true; SplitView.minimumWidth: 300; spacing: 0
            Rectangle {
                Layout.fillWidth: true; implicitHeight: 33; color: Theme.header
                RowLayout {
                    anchors.fill: parent; anchors.leftMargin: 10; anchors.rightMargin: 6; spacing: 6
                    Label { text: "3D VIEWPORT"; color: Theme.muted; font.pixelSize: 10; font.letterSpacing: 1; Layout.fillWidth: true }
                    UiButton { objectName: "addWorldImage"; glyph: "image"; flatStyle: true; hint: "Import a world reference image"+(viewport.imageAlignmentAxis ? " · "+viewport.imageAlignmentAxis+" alignment" : ""); enabled: !workspace.state.waiting && !workspace.state.editing; onClicked: imageFile.request("",viewport.imageAlignmentAxis) }
                    UiButton { text: viewport.orthographic ? "Orthographic" : "Perspective"; flatStyle: true; hint: "Toggle perspective / orthographic projection (5)"; onClicked: viewport.orthographic = !viewport.orthographic }
                    UiButton { glyph: "frame"; flatStyle: true; hint: "Frame selected (F)"; onClicked: workspace.frameSelection() }
                    UiButton { text: "Overlays"; flatStyle: true; onClicked: overlays.open() }
                }
            }
            Item {
                Layout.fillWidth: true; Layout.fillHeight: true
                Viewport { id: viewport; objectName: "viewport"; anchors.fill: parent; toolMode: window.activeTool; keyboard: keyboard; onImportRequested: importFile.open() }
                Item {
                    anchors.left: parent.left; anchors.top: parent.top; anchors.margins: 10
                    width: viewportTools.width; height: viewportTools.height
                    MouseArea { anchors.fill: parent; acceptedButtons: Qt.AllButtons }
                    Column {
                        id: viewportTools; spacing: 5
                        Repeater {
                            model: [{name:"Move",icon:"move",command:"grab"},{name:"Rotate",icon:"rotate",command:"turn"},{name:"Scale",icon:"scale",command:"resize"}]
                            UiButton { required property var modelData; objectName: "tool"+modelData.name; width: 34; height: 34; glyph: modelData.icon; enabled: viewport.transformAvailable; checkable: true; checked: enabled && window.activeTool === modelData.name && !workspace.drawingTools.state.active; hint: modelData.name+" gizmo · "+keyboard.shortcut(modelData.command)+": mouse transform"; onClicked: { workspace.drawingTools.cancel(); window.activeTool = modelData.name; } }
                        }
                        Rectangle { width: 34; height: 1; color: Theme.border }
                        CurveToolbar { keyboard: window.keyboardManager }
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
                    Label { text: workspace.state.object_count + " objects · "+workspace.state.display_units; color: Theme.muted; font.pixelSize: 11 }
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
                Rectangle {
                    id: inspectorHeader; objectName: "inspectorHeader"; property bool shortcuts: false
                    Connections { target: workspace.shortcutPanel; function onRevealRequested() { inspectorHeader.shortcuts=true; } }
                    Layout.fillWidth: true; implicitHeight: 33; color: Theme.header
                    RowLayout {
                        anchors.fill: parent; anchors.leftMargin: 8; anchors.rightMargin: 8
                        Label { text: inspectorHeader.shortcuts ? "SHORTCUTS" : "PROPERTIES"; Layout.fillWidth: true; color: Theme.muted; font.pixelSize: 10; font.letterSpacing: 1 }
                        UiButton { text: inspectorHeader.shortcuts ? "Properties" : "Shortcuts"; flatStyle: true; onClicked: inspectorHeader.shortcuts=!inspectorHeader.shortcuts }
                    }
                }
                Shortcuts { objectName: "shortcutPanel"; visible: inspectorHeader.shortcuts && !workspace.drawingTools.state.active; Layout.fillWidth: true; Layout.fillHeight: true; Layout.margins: Theme.inset }
                Inspector { id: inspector; objectName: "inspector"; visible: !inspectorHeader.shortcuts && !workspace.drawingTools.state.active; Layout.fillWidth: true; Layout.fillHeight: true; Layout.margins: Theme.inset; onPickAnchor: function(mode) { viewport.anchorMode = mode; }; onDeleteRequested: entity => deleteDialog.request(entity); onImageRequested: parentId => imageFile.request(parentId,viewport.imageAlignmentAxis) }
                UiScrollView {
                    id: drawingSettings; visible: workspace.drawingTools.state.active
                    Layout.fillWidth: true; Layout.fillHeight: true; Layout.margins: Theme.inset; contentWidth: availableWidth
                    DrawingSettings { width: drawingSettings.availableWidth; keyboard: window.keyboardManager }
                }
            }
        }
    }
    footer: Rectangle {
        color: "#25262a"; implicitHeight: 25
        RowLayout {
            anchors.fill: parent; anchors.leftMargin: 10; anchors.rightMargin: 10; spacing: 12
            Rectangle { implicitWidth: 6; implicitHeight: 6; radius: 3; color: workspace.state.blocked ? Theme.accent : Theme.success }
            Label { text: workspace.state.message || "Middle/right drag: orbit   ·   Shift-drag: pan   ·   Wheel: zoom"; color: Theme.muted; font.pixelSize: 11; elide: Text.ElideRight; Layout.fillWidth: true }
            UiButton { enabled: !!workspace.state.message; flatStyle: true; text: "Details"; implicitHeight: 22; onClicked: messageDialog.open() }
            UiButton { text: "Report folder"; enabled: !!workspace.inspectionExport.state.path && !workspace.inspectionExport.state.busy; implicitHeight: 22; onClicked: workspace.inspectionExport.showFolder() }
            Label { text: "Rev " + workspace.state.revision + (workspace.state.dirty ? " · Unsaved" : " · Saved"); color: workspace.state.dirty ? Theme.accent : Theme.muted; font.pixelSize: 11 }
        }
    }
    UiNotice { text: workspace.state.message || "" }
    ToastOverlay {}
    UiMenu {
        id: createMenu
        UiMenuItem { text: "Ordered curve loft"; onTriggered: authoring.create("LOFT","CAPSULE") }
        MenuSeparator {}
        UiMenuItem { text: "Curve-deformed box"; onTriggered: authoring.create("BODY","BOX") }
        UiMenuItem { text: "Curve-deformed cylinder"; onTriggered: authoring.create("BODY","CYLINDER") }
        UiMenuItem { text: "Curve-deformed capsule"; onTriggered: authoring.create("BODY","CAPSULE") }
        UiMenuItem { text: "Segment chain"; onTriggered: authoring.create("SEGMENT_CHAIN","CAPSULE") }
        MenuSeparator {}
        UiMenuItem { text: "Import mesh…"; onTriggered: importFile.open() }
    }
    ReferenceImageDialog { id: imageFile }
    FileDialog { id: reportDialog; title: "Export inspection report"; fileMode: FileDialog.SaveFile; defaultSuffix: "afinspection.zip"; nameFilters: ["Inspection report (*.afinspection.zip)"]; onAccepted: workspace.inspectionExport.start(selectedFile.toString()) }
    WorkspaceManager { id: workspaceManager }
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
    ShortcutHelp { id: helpDialog; keyboard: window.keyboardManager; anchors.centerIn: parent }
    FeedbackDialog { id: feedbackDialog; anchors.centerIn: parent }
    ReportBrowser { id: reportsDialog; anchors.centerIn: parent }
    UiDialog { id: messageDialog; title: "Last operation"; modal: true; anchors.centerIn: parent; width: Math.min(560, window.width-80); standardButtons: Dialog.Close; Label { width: parent.width; text: workspace.state.message; wrapMode: Text.WrapAnywhere; color: Theme.text } }
    FileDialog { id: importFile; title: "Import primitive mesh"; nameFilters: ["Mesh files (*.obj *.stl *.ply)"]; onAccepted: { window.chosenImport = selectedFile.toString(); importUnits.currentIndex = 0; importOptions.open(); } }
    FileDialog { id: openDialog; title: "Open AnthroForge project"; nameFilters: ["AnthroForge project (*.anthroforge)"]; onAccepted: workspace.requestDocument(selectedFile.toString()) }
    FileDialog { id: saveDialog; title: "Save AnthroForge project"; fileMode: FileDialog.SaveFile; defaultSuffix: "anthroforge"; nameFilters: ["AnthroForge project (*.anthroforge)"]; onAccepted: workspace.saveProject(selectedFile.toString(),""); onRejected: workspace.cancelSaveWait() }
    UiDialog {
        id: importOptions; title: "Import primitive"; modal: true; anchors.centerIn: parent; width: 420
        ColumnLayout {
            anchors.fill: parent
            Label { text: window.chosenImport; Layout.fillWidth: true; elide: Text.ElideMiddle; color: Theme.muted; ToolTip.visible: pathHover.hovered; ToolTip.text: text; HoverHandler { id: pathHover } }
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
    UiDialog {
        id: saveChoice; title: "Calculations are still running"; modal: true; anchors.centerIn: parent; closePolicy: Popup.NoAutoClose
        ColumnLayout {
            Label { text: "Choose the document revision to save." }
            UiButton { text: "Wait for queued calculations, then save"; Layout.fillWidth: true; onClicked: { saveChoice.close(); workspace.saveProject(window.blockedSavePath,"wait"); } }
            UiButton { text: "Save latest committed revision"; Layout.fillWidth: true; onClicked: { saveChoice.close(); workspace.saveProject(window.blockedSavePath,"checkpoint"); } }
            UiButton { text: "Cancel save"; Layout.fillWidth: true; onClicked: { saveChoice.close(); workspace.cancelSaveWait(); } }
        }
    }
    UiDialog {
        id: waitingDialog; title: "Finishing project operation"; modal: true; anchors.centerIn: parent; closePolicy: Popup.NoAutoClose
        visible: workspace.state.waiting
        ColumnLayout {
            BusyIndicator { running: true; Layout.alignment: Qt.AlignHCenter }
            Label { text: "Waiting for calculations or file preparation to finish.\nYou can switch to another application while AnthroForge works." }
            UiButton { text: "Cancel waiting"; onClicked: workspace.cancelSaveWait() }
        }
    }
    UiDialog {
        id: discardDialog; title: "Unsaved changes"; modal: true; anchors.centerIn: parent
        ColumnLayout {
            Label { text: "Save the current project before replacing it, or discard its changes."; width: 330; wrapMode: Text.WordWrap }
            UiButton { text: "Save and continue"; Layout.fillWidth: true; onClicked: { discardDialog.close(); workspace.afterSave(window.replacementPath); window.saveProject(); } }
            UiButton { text: "Discard and continue"; Layout.fillWidth: true; onClicked: { discardDialog.close(); workspace.replaceDocument(window.replacementPath); } }
            UiButton { text: "Cancel"; Layout.fillWidth: true; onClicked: discardDialog.close() }
        }
    }
    UiDialog {
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
    PreferencesDialog { id: preferencesDialog }
    SurfaceGroupingDialog { id: surfaceGrouping }
    KeyboardManager {
        id: keyboard; window: window; blocked: window.modalOpen || workspace.state.waiting; transforming: viewport.transforming; snapping: viewport.snapping
        numericEditing: numericEdits.active
        capabilities: ({transform:viewport.transformAvailable})
        onRequested: command => window.dispatchShortcut(command)
        onCanceled: { viewport.cancelTransform(); workspace.drawingTools.clearStroke(); workspace.tissuePainting.cancelStroke(); }
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
        reportFeedback: () => feedback.request(window),
        confirm: () => viewport.confirmTransform(),
        removeLastPoint: () => workspace.drawingTools.removeLast(),
        projection: () => viewport.orthographic = !viewport.orthographic, xray: () => viewport.xray = !viewport.xray,
        cancel: () => { workspace.cancelViewportTools(); viewport.cancelTransform(); viewport.anchorMode = ""; viewport.forceActiveFocus(); }
    })
    function dispatchShortcut(command) {
        if(!keyboard.commandEnabled(command)) return;
        if(command==="cancel" && window.activeFocusItem?.cancelEdit) { window.activeFocusItem.cancelEdit(); return; }
        const action = shortcutCommands[command];
        if (action) action();
    }
}
