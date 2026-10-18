import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

UiDialog {
    id: dialog
    required property var keyboard
    objectName: "shortcutHelp"
    title: "Navigation & shortcuts"; modal: true
    width: 580; height: Math.min(660, parent.height-40)
    standardButtons: Dialog.Close
    ScrollView {
        id: scroll
        anchors.fill: parent; clip: true; contentWidth: availableWidth; rightPadding: effectiveScrollBarWidth
        ColumnLayout {
            width: scroll.availableWidth; spacing: Theme.inset
            Repeater {
                model: [
                    {title:"View", rows:[["Middle / right drag","Orbit"],["Shift + drag","Pan"],["Wheel","Zoom"],[dialog.keyboard.shortcut("frame"),"Frame selected"],["1 / 2 / 3","X / Y / Z view · preserve current edit"],[dialog.keyboard.shortcut("restoreView"),"Restore camera before axis views"],[dialog.keyboard.shortcut("projection"),"Perspective / orthographic"],[dialog.keyboard.shortcut("xray"),"X-ray"],["Alt-click","Select through overlapping objects"]]},
                    {title:"Editing", rows:[["G / R / S","Move / rotate / scale"],["Left click / Enter","Confirm transform"],["Right click / Esc","Cancel transform or picking"],["W / E","Move / rotate gizmo"],["Delete","Remove object · preserve children"],["Shift during transform","Fine adjustment"],["Shift in curve editing","Preview insertion · click to add points"],["Ctrl during point drag","Snap to another SCP surface"],["Wheel while snapping","Adjust surface offset"],["Middle click / release Ctrl","Reset surface offset"],["Ctrl-click component","Extend selection"]]},
                    {title:"Project & diagnostics", rows:[["Ctrl+N / Ctrl+O","New / open project"],["Ctrl+S / Ctrl+Shift+S","Save / save as"],["Ctrl+I","Import mesh"],["Ctrl+Z / Ctrl+Y","Undo / redo"],[dialog.keyboard.shortcut("recordPerformance"),"Start / stop performance recording"]]}
                ]
                UiSection {
                    required property var modelData
                    title: modelData.title
                    Repeater {
                        model: modelData.rows
                        UiDetail { required property var modelData; label: modelData[0]; value: modelData[1]; labelWidth: 185
                        }
                    }
                }
            }
        }
    }
}
