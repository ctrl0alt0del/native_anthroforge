import AnthroForge.Desktop 1.0
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

ApplicationWindow {
    id: window
    width: 1440; height: 900; minimumWidth: 1050; minimumHeight: 680
    visible: true
    title: "AnthroForge — " + App.project.documentName + (App.runtime.state.dirty ? " *" : "")
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
    Connections { target: App.tissueInspection; function onFindingsRequested() { window.issuesOpen=true; window.activityOpen=false; } }
    Connections { target: App.spatialEvidence; function onFindingsRequested() { window.issuesOpen=true; window.activityOpen=false; } }
    property string activeTool: "Move"
    readonly property var keyboardManager: keyboard
    readonly property bool typing: keyboard.typing
    readonly property bool modalOpen: skeletonFile.visible || skeletonUpdateDialog.visible || assemblyFile.visible || assemblyDialog.visible || recoveryDialog.visible || tissueSourcePicker.visible || tissueRetargetReview.visible || meshReplacementReview.visible || replacementFile.visible || pinRepairDialog.visible || preferencesDialog.visible || surfaceGrouping.visible || reportsDialog.visible || feedbackDialog.visible || imageFile.visible || reportDialog.visible || importOptions.visible || saveChoice.visible || waitingDialog.visible || discardDialog.visible || closeDialog.visible || helpDialog.visible || messageDialog.visible || inspector.dialogVisible || deleteDialog.visible || importFile.visible || openDialog.visible || saveDialog.visible
    readonly property int activeJobCount: App.activityModel.activeCount
    readonly property bool jobFailed: App.activityModel.hasFailures
    function inspectScene(): string { return viewport.inspectScene(); }
    function saveProject() {
        viewport.forceActiveFocus();
        if (App.runtime.state.path) App.project.saveProject(App.runtime.state.path, "");
        else saveDialog.open();
    }
    onClosing: function(close) {
        if (App.feedback.state.busy || App.reportBrowser.state.busy || reportsDialog.editingDescription) { close.accepted=false; return; }
        if (App.runtime.state.dirty && !closingConfirmed) { close.accepted = false; closeDialog.open(); }
    }
    Action { id: newAction; text: "New project"; enabled: !window.modalOpen; onTriggered: { viewport.forceActiveFocus(); App.project.newDocument(); } }
    Action { id: openAction; text: "Open project…"; enabled: !window.modalOpen; onTriggered: { viewport.forceActiveFocus(); openDialog.open(); } }
    Action { id: saveAction; text: "Save"; enabled: !window.modalOpen; onTriggered: window.saveProject() }
    Action { id: saveAsAction; text: "Save as…"; enabled: !window.modalOpen; onTriggered: { viewport.forceActiveFocus(); saveDialog.open(); } }
    Action { id: importAction; text: "Import mesh…"; enabled: !window.modalOpen; onTriggered: importFile.open() }
    Action { id: skeletonAction; text: "Update Skeleton from Project…"; enabled: !window.modalOpen && !App.runtime.state.editing && !App.runtime.state.waiting; onTriggered: skeletonFile.open() }
    Action { id: assemblyAction; text: "Import Anatomy from Project…"; enabled: !window.modalOpen && !App.runtime.state.editing && !App.runtime.state.waiting; onTriggered: assemblyFile.open() }
    Action { id: undoAction; text: "Undo"; enabled: !window.modalOpen && !window.typing; onTriggered: App.runtime.run("undo",{}) }
    Action { id: redoAction; text: "Redo"; enabled: !window.modalOpen && !window.typing; onTriggered: App.runtime.run("redo",{}) }
    Action { id: tissueAction; text: "Create Tissue"; enabled: !window.modalOpen && !App.runtime.state.waiting && !App.selection.selectedData.readonly && !!App.selection.selectedData.tissue_presets?.length; onTriggered: App.construction.createConstruction("tissue.create",{source:App.selection.selectedData.id}) }
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
                    UiMenu {
                        title: "File"
                        UiMenuItem { action: newAction }
                        UiMenuItem { action: openAction }
                        RecentProjectsMenu { enabled: !window.modalOpen }
                        UiMenuItem { objectName:"recoverAutosaveMenu"; text:"Recover autosave…"; enabled:!window.modalOpen; onTriggered:App.projectLibrary.showRecovery() }
                        MenuSeparator {}
                        UiMenuItem { action: saveAction }
                        UiMenuItem { action: saveAsAction }
                        MenuSeparator {}
                        UiMenuItem { action: importAction }
                        UiMenuItem { objectName:"assemblyImportMenu"; action: assemblyAction }
                        UiMenuItem { objectName:"skeletonUpdateMenu"; action: skeletonAction }
                        MenuSeparator {}
                        UiMenuItem { objectName:"inspectionReportFolder"; text:"Open inspection report folder"; enabled:!!App.inspectionExport.state.path && !App.inspectionExport.state.busy; onTriggered:App.inspectionExport.showFolder() }
                        UiMenuItem { objectName:"exportInspectionMenu"; text:"Export inspection report…"; enabled:!App.inspectionExport.state.busy && !App.runtime.state.editing; onTriggered:{ viewport.storeCamera(); reportDialog.open(); } }
                    }
                    UiMenu {
                        title: "Edit"
                        UiMenuItem { action: undoAction }
                        UiMenuItem { action: redoAction }
                        MenuSeparator {}
                        UiMenuItem { text: "Delete selected"; shortcutHint: keyboard.shortcut("deleteSelection"); enabled: !!App.selection.selectedId && !App.selection.selectedData.readonly; onTriggered: deleteDialog.request(App.selection.selectedId) }
                        MenuSeparator {}
                        UiMenuItem { objectName: "preferencesMenu"; text: "Preferences…"; enabled: !window.modalOpen && !App.runtime.state.editing; onTriggered: preferencesDialog.open() }
                    }
                    UiMenu {
                        title:"Create"
                        UiMenuItem { text:"Primitive…"; onTriggered:createMenu.popup() }
                        UiMenuItem { text:"Point at cursor"; onTriggered:App.construction.createPoint() }
                        UiMenuItem { text:"Curve at cursor"; onTriggered:App.drawingTools.addCurve() }
                        UiMenuItem { text:"Place curve points"; onTriggered:App.drawingTools.begin("POINTS") }
                        UiMenuItem { text:"Place branched points"; onTriggered:App.drawingTools.begin("BRANCH") }
                        UiMenuItem { text:"Draw curve"; onTriggered:App.drawingTools.begin("DRAW") }
                        UiMenuItem { text:"Place Fiber on surfaces"; onTriggered:App.drawingTools.begin("FIBER") }
                        UiMenuItem { text:"Surface from selection"; enabled:App.construction.surfaceAction.enabled; onTriggered:App.construction.createSurface("AUTO") }
                        UiMenuItem { action:tissueAction }
                        UiMenuItem { text:"Reference image…"; onTriggered:imageFile.request("",viewport.imageAlignmentAxis) }
                    }
                    UiMenu {
                        title: "View"
                        UiMenuItem { objectName:"reconstructionMenu"; text:"Reconstruction"; checkable:true; checked:App.reconstructionPanel.opened; onTriggered:App.reconstructionPanel.setOpen(checked) }
                        UiMenuItem { objectName:"focusEditorMenu"; text:"Focus editor"; checkable:true; checked:App.workbench.focusEditor; onTriggered:App.workbench.setFocusEditor(checked) }
                        UiMenuItem { text: "Frame selected"; shortcutHint: "F"; onTriggered: App.viewport.frameSelection() }
                        UiMenuItem { objectName: "restoreViewMenu"; text: "Restore view"; shortcutHint: keyboard.shortcut("restoreView"); enabled: viewport.canRestoreView; onTriggered: viewport.restoreView() }
                        UiMenuItem { text: "Orthographic"; checkable: true; checked: viewport.orthographic; onTriggered: viewport.orthographic = checked }
                        UiMenuItem { text: "X-ray"; shortcutHint: "Alt+Z"; checkable: true; checked: viewport.xray; onTriggered: viewport.xray = checked }
                        MenuSeparator {}
                        UiMenuItem { text: "Transform handles"; checkable: true; checked: App.runtime.state.handles; onTriggered: App.runtime.run("workspace.update",{handles:checked}) }
                        UiMenuItem { text: "Attachment markers"; checkable: true; checked: App.runtime.state.anchors; onTriggered: App.runtime.run("workspace.update",{anchors:checked}) }
                        UiMenuItem { text: "Performance diagnostics"; checkable: true; checked: App.runtime.state.diagnostics; onTriggered: App.runtime.run("workspace.update",{diagnostics:checked}) }
                        UiMenuItem { text: "Activity panel"; checkable: true; checked: window.activityOpen; onTriggered: window.activityOpen = checked }
                        UiMenuItem { text: "Issues panel"; checkable: true; checked: window.issuesOpen; onTriggered: { window.issuesOpen = checked; if(checked) window.activityOpen = false; } }
                        MenuSeparator {}
                        UiMenuItem { text: App.performance.state.recording ? "Stop recording" : "Record performance"; shortcutHint: keyboard.shortcut("recordPerformance"); onTriggered: App.performance.toggle() }
                    }
                    UiMenu {
                        title: "Help"; objectName: "helpMenu"
                        UiMenuItem { objectName: "reportFeedbackMenu"; text: "Report a bug / recommendation…"; shortcutHint: keyboard.shortcut("reportFeedback"); enabled: !window.modalOpen && !App.feedback.state.active; onTriggered: App.feedback.request(window) }
                        UiMenuItem { objectName: "viewReportsMenu"; text: "View reports…"; enabled: !window.modalOpen; onTriggered: reportsDialog.open() }
                        UiMenuItem { text: "Navigation and shortcuts"; onTriggered: helpDialog.open() }
                    }
                }
                Label { text:App.project.documentName; color:Theme.muted; Layout.fillWidth:true; horizontalAlignment:Text.AlignRight; elide:Text.ElideMiddle }
                ProfileStatus { keyboard: window.keyboardManager }
            }
        }
    }
    SplitView {
        id: panels; anchors.fill: parent; orientation: Qt.Horizontal
        onResizingChanged: if(!resizing && navigationPane.visible) App.workbench.savePanes(navigationPane.width,inspectorPane.width)
        handle: Rectangle { implicitWidth: 4; color: SplitHandle.hovered || SplitHandle.pressed ? Theme.accent : "#1b1c1f" }
        Rectangle {
            id:navigationPane; visible:!App.workbench.focusEditor
            SplitView.preferredWidth: App.workbench.paneWidth("navigation",210); SplitView.minimumWidth: 195; SplitView.maximumWidth: 440
            color: Theme.panel
            ObjectBrowser {
                anchors.fill: parent; anchors.margins: Theme.inset; keyboard: window.keyboardManager
                onImportRequested: importFile.open(); onDeleteRequested: entity => deleteDialog.request(entity)
            }
        }
        Rectangle {
            visible: App.reconstructionPanel.opened && !App.reconstructionPanel.floating
            SplitView.preferredWidth: 320; SplitView.minimumWidth: 290; SplitView.maximumWidth: 520
            color: Theme.panel
            Loader { anchors.fill:parent; anchors.margins:Theme.inset; active:parent.visible; sourceComponent:reconstructionContent }
        }
        ColumnLayout {
            SplitView.fillWidth: true; SplitView.minimumWidth: 300; spacing: 0
            ViewportHeader {
                viewport:viewport; Layout.fillWidth:true
                onManageRequested:workspaceManager.open()
                onImageRequested:imageFile.request("",viewport.imageAlignmentAxis)
                onOverlaysRequested:overlays.open()
            }
            Item {
                Layout.fillWidth: true; Layout.fillHeight: true
                Viewport { id: viewport; objectName: "viewport"; anchors.fill: parent; toolMode: window.activeTool; keyboard: keyboard; onImportRequested: importFile.open() }
                UiScrollView {
                    anchors.left:parent.left; anchors.top:parent.top; anchors.bottom:parent.bottom; anchors.margins:8
                    width:50; contentHeight:viewportTools.height; contentWidth:34
                    ScrollBar.horizontal.policy:ScrollBar.AlwaysOff
                    Column {
                        id: viewportTools; spacing: 5
                        Repeater {
                            model: [{name:"Move",icon:"move",command:"grab"},{name:"Rotate",icon:"rotate",command:"turn"},{name:"Scale",icon:"scale",command:"resize"}]
                            UiButton { required property var modelData; objectName: "tool"+modelData.name; width: 34; height: 34; glyph: modelData.icon; enabled: viewport.transformAvailable; checkable: true; checked: enabled && window.activeTool === modelData.name && !App.drawingTools.state.active; hint: modelData.name+" gizmo · "+keyboard.shortcut(modelData.command)+": mouse transform"; onClicked: { App.drawingTools.cancel(); window.activeTool = modelData.name; } }
                        }
                        Rectangle { width: 34; height: 1; color: Theme.border }
                        CurveToolbar { keyboard: window.keyboardManager }
                        Rectangle { width:34; height:1; color:Theme.border }
                        UiButton { objectName:"createPrimitive"; width:34; height:34; glyph:"plus"; hint:"Create primitive"; enabled:!App.runtime.state.waiting; onClicked:createMenu.popup() }
                        UiButton { objectName:"createTissueToolbar"; width:34; height:34; glyph:"mesh"; hint:"Create tissue from selected construction"; enabled:tissueAction.enabled; onClicked:tissueAction.trigger() }
                    }
                }
            }
            Rectangle { Layout.fillWidth: true; implicitHeight: window.activityOpen ? 160 : 0; visible: window.activityOpen; color: Theme.panel; Activity { anchors.fill: parent; anchors.margins: 10 } }
            Rectangle { Layout.fillWidth: true; implicitHeight: window.issuesOpen ? 290 : 0; visible: window.issuesOpen; color: Theme.panel; Issues { anchors.fill: parent; anchors.margins: 10 } }
        }
        Rectangle {
            id:inspectorPane
            SplitView.preferredWidth: App.workbench.paneWidth("inspector",330); SplitView.minimumWidth: 280; SplitView.maximumWidth: 500
            color: Theme.panel
            RowLayout {
                anchors.fill: parent; spacing: 0
                InspectorNavigation { header: inspectorHeader }
                ColumnLayout {
                Layout.fillWidth: true; Layout.fillHeight: true; spacing: 0
                InspectorHeader { id:inspectorHeader }
                Shortcuts { objectName: "shortcutPanel"; visible: inspectorHeader.shortcuts && !App.drawingTools.state.active; Layout.fillWidth: true; Layout.fillHeight: true; Layout.margins: Theme.inset }
                Inspector { category:inspectorHeader.category; id: inspector; objectName: "inspector"; visible: inspectorHeader.page==="Shape" && !App.drawingTools.state.active; Layout.fillWidth: true; Layout.fillHeight: true; Layout.margins: Theme.inset; onPickAnchor: function(mode) { viewport.anchorMode = mode; }; onDeleteRequested: entity => deleteDialog.request(entity); onImageRequested: parentId => imageFile.request(parentId,viewport.imageAlignmentAxis) }
                InspectionPane { objectName:"inspectionPane"; visible:inspectorHeader.page==="Inspect" && !App.drawingTools.state.active; Layout.fillWidth:true; Layout.fillHeight:true; Layout.margins:Theme.inset }
                SkinPane { objectName:"skinPane"; visible:inspectorHeader.page==="Skin" && !App.drawingTools.state.active; Layout.fillWidth:true; Layout.fillHeight:true; Layout.margins:Theme.inset }
                UiScrollView {
                    id: drawingSettings; visible: App.drawingTools.state.active
                    Layout.fillWidth: true; Layout.fillHeight: true; Layout.margins: Theme.inset; contentWidth: availableWidth
                    DrawingSettings { width: drawingSettings.availableWidth; keyboard: window.keyboardManager }
                }
                }
            }
        }
    }
    Component { id:reconstructionContent; ReconstructionPane {} }
    Window {
        id:reconstructionWindow; title:"Reconstruction"; width:420; height:700; minimumWidth:320; minimumHeight:400
        color:Theme.panel; visible:App.reconstructionPanel.opened && App.reconstructionPanel.floating
        onClosing:function(event) { event.accepted=false; App.reconstructionPanel.setOpen(false); }
        Loader { anchors.fill:parent; anchors.margins:Theme.inset; active:reconstructionWindow.visible; sourceComponent:reconstructionContent }
    }
    footer: WorkbenchStatus { windowState:window; onDetailsRequested:messageDialog.open() }
    UiNotice { text: App.runtime.state.message || "" }
    ToastOverlay {}
    UiMenu {
        id: createMenu
        UiMenuItem { text: "Ordered curve loft"; onTriggered: App.authoring.create("LOFT","CAPSULE") }
        MenuSeparator {}
        UiMenuItem { text: "Curve-deformed box"; onTriggered: App.authoring.create("BODY","BOX") }
        UiMenuItem { text: "Curve-deformed cylinder"; onTriggered: App.authoring.create("BODY","CYLINDER") }
        UiMenuItem { text: "Curve-deformed capsule"; onTriggered: App.authoring.create("BODY","CAPSULE") }
        UiMenuItem { text: "Segment chain"; onTriggered: App.authoring.create("SEGMENT_CHAIN","CAPSULE") }
        MenuSeparator {}
        UiMenuItem { text: "Import mesh…"; onTriggered: importFile.open() }
    }
    ReferenceImageDialog { id: imageFile }
    FileDialog { id: reportDialog; title: "Export inspection report"; fileMode: FileDialog.SaveFile; defaultSuffix: "afinspection.zip"; nameFilters: ["Inspection report (*.afinspection.zip)"]; onAccepted: App.inspectionExport.start(selectedFile.toString()) }
    WorkspaceManager { id: workspaceManager }
    Popup {
        id: overlays; x: Math.max(0,window.width-650); y: 110; padding: 14
        background: Rectangle { color: Theme.panel; border.color: Theme.border; radius: 6 }
        ColumnLayout {
            Label { text: "VIEWPORT OVERLAYS"; color: Theme.muted; font.pixelSize: 10 }
            UiCheck { text: "Transform handles"; checked: App.runtime.state.handles; onClicked: App.runtime.run("workspace.update",{handles:checked}) }
            UiCheck { text: "Attachment markers"; checked: App.runtime.state.anchors; onClicked: App.runtime.run("workspace.update",{anchors:checked}) }
            UiCheck { text: "Performance diagnostics"; checked: App.runtime.state.diagnostics; onClicked: App.runtime.run("workspace.update",{diagnostics:checked}) }
        }
    }
    ShortcutHelp { id: helpDialog; keyboard: window.keyboardManager; anchors.centerIn: parent }
    FeedbackDialog { id: feedbackDialog; anchors.centerIn: parent }
    ReportBrowser { id: reportsDialog; anchors.centerIn: parent }
    UiDialog { id: messageDialog; title: "Last operation"; modal: true; anchors.centerIn: parent; width: Math.min(560, window.width-80); standardButtons: Dialog.Close; Label { width: parent.width; text: App.runtime.state.message; wrapMode: Text.WrapAnywhere; color: Theme.text } }
    FileDialog { id: importFile; title: "Import primitive mesh"; nameFilters: ["Mesh files (*.obj *.stl *.ply)"]; onAccepted: { window.chosenImport = selectedFile.toString(); importUnits.currentIndex = 0; importOptions.open(); } }
    FileDialog { id: openDialog; title: "Open AnthroForge project"; nameFilters: ["AnthroForge project (*.anthroforge)"]; onAccepted: App.project.requestDocument(selectedFile.toString()) }
    FileDialog { id: saveDialog; title: "Save AnthroForge project"; fileMode: FileDialog.SaveFile; defaultSuffix: "anthroforge"; nameFilters: ["AnthroForge project (*.anthroforge)"]; onAccepted: App.project.saveProject(selectedFile.toString(),""); onRejected: App.project.cancelSaveWait() }
    UiDialog {
        id: importOptions; title: "Import primitive"; modal: true; anchors.centerIn: parent; width: 420
        ColumnLayout {
            anchors.fill: parent
            Label { text: window.chosenImport; Layout.fillWidth: true; elide: Text.ElideMiddle; color: Theme.muted; ToolTip.visible: pathHover.hovered; ToolTip.text: text; HoverHandler { id: pathHover } }
            Label { text: "Source units (required)" }
            UiCombo { id: importUnits; Layout.fillWidth: true; model: ["Choose source units…","Metres","Centimetres","Millimetres"] }
            Label { text: "Parent SCP"; visible: App.selection.treeRows.length > 0 }
            UiCombo { id: importParent; visible: App.selection.treeRows.length > 0; Layout.fillWidth: true; model: App.selection.treeRows.filter(row => !row.is_control); textRole: "name"; valueRole: "id"; currentIndex: Math.max(0,indexOfValue(App.selection.selectedId)) }
            UiCheck { id: sourceYUp; text: "Convert Y-up source to Z-up" }
            Label { text: "One SCP per file. Geometry only; materials and textures are ignored."; Layout.fillWidth: true; wrapMode: Text.WordWrap; color: Theme.muted }
            RowLayout {
                Item { Layout.fillWidth: true }
                UiButton { text: "Cancel"; onClicked: importOptions.close() }
                UiButton {
                    text: "Import"; enabled: importUnits.currentIndex > 0
                    onClicked: { App.project.importMesh(window.chosenImport,[0,1,.01,.001][importUnits.currentIndex],App.selection.treeRows.length ? importParent.currentValue : "",sourceYUp.checked); importOptions.close(); }
                }
            }
        }
    }
    UiDialog {
        id: saveChoice; title: "Calculations are still running"; modal: true; anchors.centerIn: parent; closePolicy: Popup.NoAutoClose
        ColumnLayout {
            Label { text: "Choose the document revision to save." }
            UiButton { text: "Wait for queued calculations, then save"; Layout.fillWidth: true; onClicked: { saveChoice.close(); App.project.saveProject(window.blockedSavePath,"wait"); } }
            UiButton { text: "Save latest committed revision"; Layout.fillWidth: true; onClicked: { saveChoice.close(); App.project.saveProject(window.blockedSavePath,"checkpoint"); } }
            UiButton { text: "Cancel save"; Layout.fillWidth: true; onClicked: { saveChoice.close(); App.project.cancelSaveWait(); } }
        }
    }
    UiDialog {
        id: waitingDialog; title: "Finishing project operation"; modal: true; anchors.centerIn: parent; closePolicy: Popup.NoAutoClose
        visible: App.runtime.state.waiting
        ColumnLayout {
            BusyIndicator { running: true; Layout.alignment: Qt.AlignHCenter }
            Label { text: "Waiting for calculations or file preparation to finish.\nYou can switch to another application while AnthroForge works." }
            UiButton { text: "Cancel waiting"; onClicked: App.project.cancelSaveWait() }
        }
    }
    UiDialog {
        id: discardDialog; objectName: "discardDialog"; title: "Unsaved changes"; modal: true; anchors.centerIn: parent
        ColumnLayout {
            Label { text: "Save the current project before replacing it, or discard its changes."; width: 330; wrapMode: Text.WordWrap }
            UiButton { text: "Save and continue"; Layout.fillWidth: true; onClicked: { discardDialog.close(); App.project.afterSave(window.replacementPath); window.saveProject(); } }
            UiButton { text: "Discard and continue"; Layout.fillWidth: true; onClicked: { discardDialog.close(); App.project.replaceDocument(window.replacementPath); } }
            UiButton { text: "Cancel"; Layout.fillWidth: true; onClicked: discardDialog.close() }
        }
    }
    UiDialog {
        id: closeDialog; title: "Close with unsaved changes?"; modal: true; anchors.centerIn: parent
        standardButtons: Dialog.Save | Dialog.Discard | Dialog.Cancel
        Label { text: "Save your project to keep these changes." }
        onAccepted: { App.project.afterSave("@close"); window.saveProject(); }
        onDiscarded: { window.closingConfirmed = true; window.close(); }
    }
    Connections {
        target: App.project
        function onSaveChoiceRequested(path) { window.blockedSavePath = path; saveChoice.open(); }
        function onDiscardRequested(path) { window.replacementPath = path; discardDialog.open(); }
        function onCloseReady() { window.closingConfirmed = true; window.close(); }
    }
    DeleteDialog { id: deleteDialog }
    PreferencesDialog { id: preferencesDialog }
    RecoveryDialog { id: recoveryDialog }
    Connections { target:App.projectLibrary; function onRecoveryRequested() { recoveryDialog.open(); } }
    SurfaceGroupingDialog { id: surfaceGrouping }
    FileDialog { id:replacementFile; objectName:"replacementFile"; title:"Replace imported source mesh"; nameFilters:["Wavefront mesh (*.obj)"]; onAccepted:App.meshReplacement.assess(selectedFile.toString()); onRejected:App.meshReplacement.cancel() }
    TissueSourcePicker { id:tissueSourcePicker }
    ReplacementReview { id:tissueRetargetReview; objectName:"tissueRetargetReview"; service:App.tissueRetarget }
    MeshReplacementReview { id:meshReplacementReview; onChooseFile:replacementFile.open() }
    SkeletonUpdateDialog { id: skeletonUpdateDialog }
    VariantReviewDialog {}
    ReconstructionCompareDialog {}
    FileDialog { id:skeletonFile; title:"Update Skeleton from Project"; nameFilters:["AnthroForge project (*.anthroforge)"]; onAccepted:App.skeletonPanel.inspect(selectedFile.toString()) }
    FileDialog { id:assemblyFile; title:"Import Anatomy from Project"; nameFilters:["AnthroForge project (*.anthroforge)"]; onAccepted:App.assemblyPanel.inspect(selectedFile.toString()) }
    AssemblyDialog { id:assemblyDialog }
    FiberPinReview { id:pinRepairDialog }
    Connections { target:App.issuePanel; function onPinReviewRequested(curve) { pinRepairDialog.request(curve); } }
    KeyboardManager {
        id: keyboard; window: window; blocked: window.modalOpen || App.runtime.state.waiting; transforming: viewport.transforming; snapping: viewport.snapping
        numericEditing: App.numericEdits.active
        capabilities: ({transform:viewport.transformAvailable})
        onRequested: command => window.dispatchShortcut(command)
        onCanceled: { viewport.cancelTransform(); App.drawingTools.clearStroke(); App.tissuePainting.cancelStroke(); }
        onOffsetRequested: steps => viewport.surfaceOffset(steps)
        onOffsetReset: viewport.resetSurfaceOffset()
    }
    readonly property var shortcutCommands: ({
        new: () => newAction.trigger(), open: () => openAction.trigger(), save: () => saveAction.trigger(),
        saveAs: () => saveAsAction.trigger(), importMesh: () => importAction.trigger(),
        undo: () => undoAction.trigger(), redo: () => redoAction.trigger(),
        deleteSelection: () => deleteDialog.request(App.selection.selectedId), frame: () => App.viewport.frameSelection(),
        move: () => activeTool = "Move", rotate: () => activeTool = "Rotate", scale: () => activeTool = "Scale",
        grab: () => viewport.startModalTransform("Move"), turn: () => viewport.startModalTransform("Rotate"), resize: () => viewport.startModalTransform("Scale"),
        viewX: () => viewport.setView("Right"), viewY: () => viewport.setView("Front"), viewZ: () => viewport.setView("Top"),
        restoreView: () => viewport.restoreView(),
        recordPerformance: () => App.performance.toggle(),
        reportFeedback: () => App.feedback.request(window),
        confirm: () => viewport.confirmTransform(),
        removeLastPoint: () => App.drawingTools.removeLast(),
        projection: () => viewport.orthographic = !viewport.orthographic, xray: () => viewport.xray = !viewport.xray,
        cancel: () => { App.viewport.cancelViewportTools(); viewport.cancelTransform(); viewport.anchorMode = ""; viewport.forceActiveFocus(); }
    })
    function dispatchShortcut(command) {
        if(!keyboard.commandEnabled(command)) return;
        if(command==="cancel" && window.activeFocusItem?.cancelEdit) { window.activeFocusItem.cancelEdit(); return; }
        const action = shortcutCommands[command];
        if (action) action();
    }
}
