# Editor polish — 0.1.9

Menus now use dark hover and pressed states, aligned checkmarks and a separate
shortcut column. Buttons, fields and dropdowns share a 30-pixel control height;
dropdown rows fit within their popup padding. Dialog buttons and scrollbars follow
the same styling, with space reserved for scrolling rather than covering controls.

The newer inspection tools show a concise summary first:

- **Measurements & views:** distances stay visible. Press **+** beside a ruler
  to show its A, B and delta coordinates; press **−** to collapse them.
- **Relationships & attachments:** result, support and surface counts come first.
  Expand **Attachment details** for revisions, anchors and captured surface data.
- **Issues:** target navigation and repair actions come first. Expand
  **Details & evidence** for the full explanation, provider and diagnostic evidence.
- **Workspace & presentation:** Show and Select have aligned columns. Expand
  **Workspace members** when editing membership.
- **Help → Navigation and shortcuts:** shortcuts are grouped into View, Editing,
  and Project & diagnostics. Scroll or collapse sections to reach another group.

The **?** buttons explain controls on hover, keyboard focus or click. Thickness
and Display & evaluation start collapsed when they are not the primary editing task.
All existing editing operations, annotations and diagnostics remain available.

## Maintaining the presentation

Shared controls in `src/anthroforge/desktop/qml` own colors, focus/hover states,
padding and scrolling. Feature panels own labels, grouping and disclosure state.
They do not introduce document changes or new calculation policies.

Run `tools/ui_polish_acceptance.py` for real QML menu contrast, popup containment,
measurement disclosure, issue evidence and normal/compact layouts. To avoid desktop
windows or input interference on Windows, use an isolated process environment:

```powershell
$env:QT_QPA_PLATFORM='offscreen'
$env:QT_QPA_FONTDIR='C:\Windows\Fonts'
.venv/Scripts/python.exe tools/ui_polish_acceptance.py
```

Off-screen captures validate controls and layout, but do not establish native-window
behavior or Quick 3D surface rendering. Use the normal desktop acceptance when the
computer is available for interactive testing. Captures are local under
`build/ui-polish-019`; they are not committed to Git.

The portable check also accepts `--offscreen` after its executable and output-directory
arguments. It explicitly selects off-screen Qt for smoke/profiler sessions, keeps the
minimal PATH check, and still validates GPU surface pixels using the application's
hidden `QQuickRenderControl` capture. Its report distinguishes this from native-window
testing. Do not run the default portable check while someone is using the desktop.
