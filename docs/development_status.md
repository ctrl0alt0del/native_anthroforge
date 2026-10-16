# AnthroForge 0.1 validation

Implementation and checks performed on 2026-10-16, Windows 11 x64. The original Blender addon
was read and exercised in a separate background process; its source and user scenes were
not edited. No Git remote was contacted through Git and no commits or PRs were created.

## Implemented

The imported-SCP editor includes OBJ/STL/PLY, canonical units, single-root hierarchy,
TRS/gizmos, attachments/locks/recapture/origin relocation, update modes, independent
copies, undo transactions, revision-aware asynchronous work, checkpoint saving, embedded
project storage, focused workspaces, visibility/picking, diagnostics and JSON authoring.
See quickstart.md for the complete user walkthrough and explicit release boundaries.

## Evidence

| Check | Observed result |
| --- | --- |
| Native engine and Qt geometry plugin | clang-cl Release build and CTest passed |
| Python checks | Ruff, configured strict mypy and 143 tests passed |
| Authored function rules | Python, native clang-tidy and PowerShell checks passed |
| Blender-reference attachment comparison | 72 cases; maximum matrix element difference 2.74e-6; acceptance 3e-5 |
| Actual mouse interaction | QTest drag changed the document, created one undo entry, and undo restored the prior transform |
| Desktop persistence | Asynchronous save/reopen preserved the assembly, without QML warnings |
| Visible geometry | Cube assembly and anatomical maxilla captures inspected visually |
| Numerical headless | Import/attachment/save/inspect flow; no Qt or Blender import |
| JSON line server | Publishes background results while waiting for the next request |
| Portable distribution | PySide deployment/Nuitka; relocated minimal-PATH import/save/inspection, GPU capture and desktop checks passed, including surface-pixel assertions; both final captures inspected |

tools/check.ps1 is the repeatable development gate. tools/gui_acceptance.py and
tools/check_portable.py are separate desktop/runtime acceptance gates. Their logs and PNGs
are local build artifacts; they are not source files or evidence of remote CI execution.

Blender reference generation: tools/capture_addon_parity.py, Blender 5.0.1
(a3db93c5b259). Cases cover both parent anchor modes, all three child anchor modes,
all three rotation strategies, follow rotation on/off and positive/nonuniform/reflected
parent scale. The fixture is tests/fixtures/addon_attachments.json. It is a synthetic
oblique tetrahedron, not production anatomy. Tests additionally cover locks, origin
preservation, freeze/rebind, queue overlap, failure, cancellation, saving and undo/redo.

The unchanged source native/migration/attachment_wave_reference.hpp was copied from
the addon's native/fiber_ccd/af_attachment_wave.hpp:
SHA-256 5BAF4DD3681EE327BF184639EAA2A8386DA43228004BE55345988E6F17097750.
Comparison found and corrected triangle corner reordering and negative-scale decomposition
in the new adapters. This qualifies these attachment cases, not all future addon features.

## Viewport measurement

Input: local BodyParts3D_v3_FMA53649_right_maxilla.stl, 14,148 triangles, 32 overlapping
instances (452,736 drawn triangles), 2160 x 1350 capture. During 90 mouse orbit updates:
mean frame interval 18.46 ms (about 54 FPS), p95 25.34 ms, maximum 35.92 ms; picking
p95 0.1115 ms; GUI tick p95 11.70 ms. No QML warnings. The script explicitly pumps the
event loop between input events and uses a high-resolution clock.

This is a local rendering/picking stress fixture with shared geometry and overlap.
It is not a full-body benchmark, a claim of 50 ms end-to-end input latency, or a guarantee
for arbitrary imports. The soft responsiveness targets remain goals for future feature work.

## Filesystem incident

E:/development/anthroforge began rejecting new files/directories with Windows error 112
while reporting about 70 GB free. The cause is unresolved. Source was preserved and work
continued in C:/Users/alexe/AppData/Local/Temp/anthroforge-01-work. Writes later recovered,
and the completed source was copied back to E:/development/anthroforge. The final native
build and development checks passed there. E: rejected large packaging copies again,
so the final Windows package was built in the temporary C: directory from matching source
and copied back to the project's dist folder. The cause was not established. Automatic review rejected removal
of a regenerable E: build cache, stating only "blocked by policy"; it was left in place.

The portable build initially failed with the installed MSVC toolset and with an overly
long MinGW cache path. Explicit MinGW selection and a short user-local Nuitka cache produced
the executable. The native C++ build still uses clang-cl; these are separate build stages.

The initial QT_QPA_PLATFORM=offscreen capture silently used software rendering and had
missing fonts/3D surfaces. It was rejected after visual inspection. Capture now uses
QQuickRenderControl with an owned GPU texture and readback, without showing a window.
Its metadata records the exact revision, finite scene geometry and window visibility;
portable acceptance also requires visible cube surface pixels. A successful exit code
or nonempty PNG alone is not capture acceptance.

## UI refresh — 2026-10-16

The desktop now uses a charcoal theme with compact vector-icon controls, classic menus,
resizable panels, searchable/collapsible outliner, grouped properties with named enum
choices, axis-colored transform fields, viewport tools and orientation shortcuts, an
optional reference grid, and a collapsible activity area. Editor styling stays in QML;
the application and numerical contracts are unchanged.

tools/ui_acceptance.py exercises actual keyboard/mouse input: text-safe shortcuts,
search, numeric commit/undo without reapplying on later blur, hierarchy and property
collapse, view orientation, splitter dragging, compact 1050x680 and normal 1440x900
layouts, and the empty document. Captures were inspected. tools/gui_acceptance.py
continues to cover transform drags, one-step undo, and asynchronous save/reopen.
The full development gate passed with all 143 tests after the refresh. The updated
portable app also passed numerical, desktop, and GPU capture checks with a minimal PATH;
the final desktop image was inspected without QML warnings.

The reference conventions are Blender's area/topbar/status-bar layout and Maya's
compact attribute editing. The implementation uses Qt Quick Controls and SplitView;
icons are project-authored SVGs. This does not reproduce either product's complete UI.

## Scope limits

Only Windows was executed locally. The CI workflow is prepared but was not run remotely.
No skin/export, curve primitive construction, Blender-project conversion, linked mirroring,
crash recovery or persisted undo is claimed. See the confirmed specification for future work.
