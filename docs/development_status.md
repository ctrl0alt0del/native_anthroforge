# AnthroForge development validation

Current release qualification is in [Runtime profiler 0.1.4](#runtime-profiler-014).
The earlier sections retain the evidence and limitations of their respective revisions.

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

## Dropdown and viewport refinement — 2026-10-16

Dropdown indicators now use a vertically centered SVG chevron instead of a font
glyph. Imported meshes are opaque by default, with camera-relative studio lights,
less ambient fill and much less selection emission. This preserves authored colors
while making faces and concavities easier to read. X-ray is an explicit temporary
view setting (button, View menu, or Alt+Z); outside-workspace context remains faint
and unpickable. Transform handles now refresh their projected positions after
camera movement and framing, instead of remaining at stale screen coordinates.

Compared selected and unselected cubes and the 14,148-triangle right-maxilla fixture
before and after; inspected X-ray, focused context and compact/full-size properties.
The grid/cube overlap is physical intersection with the Z=0 reference plane, not
evidence of failed opaque depth testing. An extra depth prepass and an ambient
occlusion trial were not retained. Captures are in build/shading-before,
build/shading-final, build/ui-xray.png and build/visual-portable.

The full development gate passed (143 tests), alongside actual mouse drag/undo and
save/reopen acceptance. UI acceptance also checks X-ray by mouse and shortcut,
text-entry isolation and unchanged document state. The updated portable QML passed
minimal-PATH numerical, desktop and GPU-capture checks without QML warnings.
The same 32-instance navigation fixture measured a 20.17 ms mean frame interval
(about 50 FPS), 35.01 ms p95 and 0.1092 ms picking p95. This is a local validation
sample, not evidence of a performance improvement over the earlier run.

## Task coordination and parent/child updates — 2026-10-16

One TaskCoordinator now owns job lifecycle, worker capacity, output reservations,
publication and checkpoints. Dedicated attachment, mesh-import, project-open and
project-save schedulers assess metadata before admission and again at dispatch.
Attachment estimates include current document packing, affected objects and recapture
counts; measured timings refine subsequent estimates. File operations remain workers
with zero artificial delay. See architecture.md for the policy limits and extension points.

Bounded Live attachment work can complete before the transform command returns, using
the same native evaluator and publication checks as worker jobs. Larger interactive
requests coalesce for 16–100 ms according to estimated cost. Replacements preserve the
first pending time, including across authored invalidation; resource contention may add
queue time. Diagnostics expose estimated/actual costs, delay and execution mode.

The final development gate passed: Ruff, strict mypy, native build/CTest, style checks,
161 Python tests, numerical headless checks and native discovery. Added regression cases
cover immediate propagation, shared inline budget, measured overruns, fresh dispatch
inputs, complexity changes while queued, maximum coalescing age, overlapping writers,
publication gates, save snapshot estimation, pending-save behavior and undo cancellation.
Actual GUI drag/undo/save/reopen and the UI interaction checks passed without QML warnings.

tools/scheduling_acceptance.py observed the two-cube viewport model at frame signals
during 20 actual mouse-drag updates. All 20 updates completed inline; 29 frame observations
showed a maximum relative parent/child offset error of 3.33e-16 m. The slowest update took
0.175 ms (rounded up). Running the same fixture with background-only policy exposed
0.0396 m of relative lag. Captures were inspected. This verifies coherence on this fixture;
it does not measure end-to-end input-to-photon latency or qualify arbitrary anatomy.

Synthetic 10-update probes at 16 and 64 entities stayed inline, with maximum observed
costs of 0.451 and 1.242 ms. At 256 entities all updates used workers; maximum observed
cost was 7.783 ms and planned delay was 34.607 ms. These are local tuning evidence,
not hard execution bounds. Synchronous work cannot be forcibly preempted; timing
feedback demotes subsequent similar requests after an overrun.

The portable executable was rebuilt on E: from matching final source. Minimal-PATH
native discovery, import, attachment, save/inspect, GPU capture and desktop checks passed;
the desktop capture was inspected. A separate compiled batch verified dedicated import
policies and both immediate attachment edits through the packaged authoring API.
Runtime reports and captures are in build/coordinator-portable. The corresponding source
archive was refreshed after these changes.

## Primitive and deformer release 0.1.2

Implemented on Windows x64 against the confirmed primitives_012.md contract. The release
includes editable imported, connected-loft and curve-deformed body definitions; shared
Hook controls and lattice cages; ordered bindings; Simple Solidify; component editing;
and the same operations through the headless API. Apply/Bake has no command or UI action.
The runnable examples/primitives.json builds a connected shell, a shared cage with a Hook,
a curved capsule and an imported cube, then saves the editable document.

The implementation separates authored construction revisions, SCP poses, accepted geometry
results and presentation. Schema 2 stores source data, all parameters and shared relationships
with the selected revision's accepted meshes. Schema 1 migrates to imported definitions.
Object writers remain exclusive, while dependency reads distinguish pose, control, cage
and geometry outputs. Manual prerequisites supply accepted results with pending provenance;
actual cycles terminate unsuccessfully without suppressing unrelated components.

### Qualification evidence

| Check | Evidence |
| --- | --- |
| Development gate | Ruff, configured strict mypy, native Release build/CTest, native/script function checks, 352 Python tests, numerical headless checks and native discovery passed |
| Native reference coverage | 141 primitive/deformer comparisons: 49 curve/anatomical checks and 92 modifier/resize/shell checks, plus the existing 72 attachment comparisons |
| Actual anatomical references | Rib and mandible sampling, clavicle Hook continuity, brow cage/Hook/tilt and pelvic closed curves; compact pinned fixtures include source hashes |
| Construction and topology | Shared loft seams, caps, thickness winding, canonical triangulation, target-stage ordering, topology locks/unlocking through both application and inspector |
| Lifecycle | Mixed update modes, pending Manual inputs, missing inputs, real cycles, capture-only reads, overlapping writers, dispatch snapshots, cancellation, undo/redo, checkpoint saves and geometry collection |
| Persistence | Schema-1 migration and schema-2 round trips retain original imported vertices, editable curves, controls, sharing and accepted results |
| Desktop workflow | Creation, curve pointer hover/click/Shift selection, inspector synchronization, lattice edits, Hook weights, body-base targeting, hidden/unpickable controls, save/reopen; no QML warnings |
| Coordinate frames | Connected endpoints survive owner motion; follow changes and origin relocation preserve world placement; control gizmo motion under a rotated SCP follows its displayed world axis and undoes coherently |
| Complete example | The headless batch produces all three primitive families; the saved connected loft and curved capsule were inspected in the production GUI |
| Group framing | Empty groups frame visible descendant geometry; native bounds cover rotation, reflected scale and relocated geometry origins |
| Existing editor regression | Mouse drag/undo, save/reopen, text-safe shortcuts, layout/inspector interactions and parent/child scheduling acceptance passed without QML warnings |
| Portable Windows runtime | Final Nuitka executable relocated to a separate C: folder passed native discovery, imports, attachments, primitive/deformer construction, save/inspect, GPU capture and desktop smoke checks with a minimal PATH; final images inspected |
| Distribution | Product/file version 0.1.2.0, Python wheel resource checks and corresponding AnthroForge-0.1.2-source.zip contents verified |

Blender references use 5.0.1, build a3db93c5b259. Synthetic and source-scene JSON fixtures
are under tests/fixtures/primitives; generators are maintained under tools. Numerical
tolerances are explicit in the tests (typically 2e-5, with 5e-5 for source-scene sampling).
Connected loft boundaries are intentionally different from the disconnected Blender
node strips and have separate topology checks. These comparisons qualify their exercised
settings, not arbitrary Blender scenes. Original source .blend files were not saved or
changed. Their verified SHA-256 values are:

- skull_muscles.blend: `4855042F259135C569C3E89B50DF5D0441E6794BEF5E774AEBF924FD8372287E`
- skeleton_comb_base.blend: `1049C9CEF5D0E94735E20E1F3E313CDB845A67C6554CCF3A98E81DA98B813FF2`

### Responsiveness measurements

tools/primitive_acceptance.py --performance exercises a shell with 66,560 vertices,
133,116 triangles, nine render chunks and 1,000 cage points in a 1500 x 950 window.
It performs 19 edits, including 18 rapid superseding edits, and 120 native component picks.
The previous complete mesh remained visible throughout staged replacement. The local run
recorded the following values; milliseconds are wall-clock measurements, not guarantees.

| Operation | Samples | Mean ms | p95 ms | Maximum ms |
| --- | ---: | ---: | ---: | ---: |
| Edit command, including UI refresh | 19 | 25.14 | 43.69 | 44.48 |
| Dispatch preparation | 18 | 0.048 | 0.077 | 0.079 |
| Result adoption | 4 | 0.392 | 0.438 | 0.487 |
| Component picking | 120 | 0.027 | 0.040 | 0.139 |
| Cancellation request | 62 | 0.004 | 0.009 | 0.017 |
| Cancellation completion | 34 | 11.56 | 34.02 | 47.72 |
| Frame interval | 73 | 32.31 | 56.50 | 68.37 |

The two completed native construction jobs took 467.80 and 526.40 ms. Queued cancellation
and active-worker cancellation share the completion sample set; it is not a worst-case
native interruption bound. Initial uncached inspector/publication refresh measured about
264.6 ms mean and 342 ms p95 per edit on this fixture. Caching presentation snapshots and
separating geometry notifications from activity updates removed that repeated work.
The final sample is approximately 31 FPS on average, but p95 frame intervals exceed the
soft 30 FPS goal. This test does not measure OS input-to-photon latency or a full-body model.

### Ownership and coupling review

Reviewed separately from test results. core records own immutable authored data and accepted
provenance; construction_policy and application commands enforce topology and workspace rules
for every client. Native adapters own numerical work and return complete buffers/BVHs.
Task-specific policies estimate work; TaskCoordinator alone owns admission, output reservations,
cancellation and publication. Dependency ports and capture-only observations avoid both
whole-object invalidation and false pose/geometry cycles. Publication merges its declared
outputs into current state rather than overwriting a newer unrelated edit.

Geometry reachability covers current state, undo entries, checkpoints and running snapshots;
viewport staging and displayed frames lease native handles separately. GUI components own
selection and presentation, not alternate deformation rules. The existing SCP asset field
remains a compatibility alias for accepted geometry; central geometry queries replace
imported-asset assumptions. Thin dynamic Qt adapters remain outside the strict application
typing boundary. Initial scheduler coefficients are heuristics refined by measured costs,
and cancellation is cooperative at native checkpoints, not preemptive.

Local qualification reports and inspected images live in build/primitive-review. The
maintained tools reproduce them; generated reports and production anatomical binaries
are not included as source fixtures. Native provenance and source hashes are recorded in
native/migration/BLENDER_PRIMITIVES.md and blender_501_sources.json, with original attribution.
The final relocated-runtime report and captures are under build/primitive-review/portable-final;
the delivered executable is dist/AnthroForge.dist/AnthroForge.exe. Preserve the entire
portable folder when moving it. No Git remote operations or commits were performed.

## Current scope limits

Only Windows was executed locally. The CI workflow is prepared but was not run remotely.
No skin/export, Blender-project conversion, linked mirroring,
crash recovery or persisted undo is claimed. See the confirmed specification for future work.


## Usability release 0.1.3

Implemented and inspected on Windows 11 x64, 2026-10-17. This release changes the existing
editing workflow; it adds no primitive families. The original addon deletion implementation
was inspected: it cleared invalid parent references rather than promoting children. The
standalone now implements the user's requested promotion semantics, including the confirmed
empty grouping root replacement.

- Move: world-axis arrows, plane handles and a view-plane center. Rotate: world-axis rings.
  Scale: local-axis squares and a uniform center. Shift provides precision; Escape cancels.
  Shared deltas compose world rotation correctly and preserve negative scale and pivots.
- Curve-edit transparency is temporary presentation. The selected SCP's orange silhouette
  comes from a depth-tested selection mask and screen-space edge dilation; open lofts,
  curved bodies and imported meshes were inspected in actual GUI captures.
- Central shortcut registry and context policy cover existing shortcuts and Delete. A shared
  dialog serves keyboard, tree and inspectors. Text entry, modal dialogs, active drags and
  blocked saves retain their interaction boundaries.
- Core deletion preserves children/world poses, recaptures their new attachments, detaches
  referenced controls, rejects obsolete output and reschedules surviving dependencies.
  Root replacement, empty documents, focused workspaces, undo/redo and save/reopen are covered.

### Validation evidence

The development gate passed: 364 Python tests, strict typing, Ruff, native build/contract,
clang-tidy, script checks, numerical imports and native doctor. Existing Blender fixture
parity remains passing. The native style run prints upstream-header warning totals; there
were no failing authored-code diagnostics.

`tools/usability_acceptance.py` passed real pointer checks for 45-degree rotation in orthographic and perspective views, axis and
uniform scaling, two-axis/free movement, coherent undo and Escape rollback. It also passed
text-field Delete protection, modal shortcut blocking, keyboard root deletion, tree deletion
and opacity restoration without an authored edit. No QML warnings were reported.
Existing UI, scheduling and primitive interaction/workshop acceptance passed. The scheduling
check observed 20/20 small attachment updates inline with maximum parent-child displacement
error below 3e-16 metres.

`tools/usability_acceptance.py --render` qualified a 512-sample/64-strip thick loft with a
1,000-point cage. The old complete surface remained displayed during staging. Mask delegate
counts matched displayed/staged mesh delegates after replacement, deletion and undo, confirming
that the additional scene does not retain deleted resources. The mask shares the main geometry
objects instead of rebuilding mesh buffers.

The paired orbit run measured frame intervals with outline enabled at mean 17.3 ms / p95
30.8 ms, versus 23.8 / 38.8 ms without it in the preceding pass. These are short, order-sensitive
GUI measurements, not evidence that the added pass speeds rendering up. The large edit command
took 23.6 ms; measured result publication was below 0.5 ms. Full interaction/capture runs include
startup, file operations and screenshot stalls and had p95 intervals around 75–82 ms. These data
support the soft responsiveness goals for the measured orbit, not a universal FPS guarantee.
Captures and machine-readable reports are in ignored `build/usability-review`.

### Ownership review

Reviewed directly in this task, separately from test results. Keyboard mapping/context policy,
gizmo geometry/hit testing, paint, transform application, deletion semantics and silhouette
rendering have distinct owners. Both desktop and headless deletion use application commands.
No authored state carries hover, outline or editing opacity. Native geometry ownership and
staged publication remain authoritative; the new render pass follows the same active chunks.
The existing axis-drag API is retained as a compatibility adapter. No speculative scheduler,
renderer replacement or duplicate hierarchy implementation was introduced.


A perspective-only diagnostic exposed about 5 degrees of error in the first projected-ellipse
rotation approximation. It was replaced with mouse-ray/rotation-plane intersection. The
final 45-degree perspective gesture measured 44.57 degrees with integer-pixel mouse input;
orthographic and perspective regression checks both pass. Edge-on rings retain a screen
tangent interaction where a ray-plane intersection is ill-conditioned.

### Distribution qualification

The Nuitka portable build is `dist/AnthroForge.dist/AnthroForge.exe`, product/file version
0.1.3.0. A fresh copy at `C:/Users/alexe/AppData/Local/Temp/anthroforge-013-qualified`
passed with a minimal PATH and no development Python/Qt settings: imports, attachments,
primitive/deformer evaluation, single-SCP and root deletion, saving, inspection, GPU capture
and GUI smoke checks. The compiled deletion check saved/reopened the promoted hierarchy.
The packaged desktop was visually inspected, including its selected geometry outline.
Reports are under `build/usability-review/portable`. Packaged QML/JavaScript/icons match
the tested sources byte-for-byte. The shader is embedded in the native viewport DLL.

The wheel, source distribution and `dist/AnthroForge-0.1.3-source.zip` were regenerated;
the archive includes the new interaction, deletion and shader sources and excludes the
unrelated legacy root `__init__.py`. Changes remain uncommitted. No Git remote operations
were performed.


### Curve editing follow-up (2026-10-17)

The 0.1.3 follow-up adds held insertion preview, repeated left-click confirmation,
Ctrl surface snapping during direct-point and Move-gizmo drags, and distinct curve/point/handle
colors. Modifier bindings belong to the keyboard manager and can be rebound independently of
interaction code. Ctrl-click extends selection; its click action is deferred so holding Ctrl
before dragging a selected point still starts a snap gesture.

The development gate passed with **387 tests**, including open/closed subdivision with all four
handle modes, transformed closest-curve queries, invalid requests, unchanged attachment mesh
connectivity, undo, editable persistence and held-input lifecycle. Existing native Blender
reference comparisons remain passing. Native/style/type checks passed.

`tools/curve_interaction_acceptance.py` passed actual Qt keyboard/mouse gestures for repeated
insertion, release cancellation, switching snap targets, self exclusion, read-only focused
workspace context, snapping with Ctrl pressed before or during a drag, modifier rebinding,
text-focus suppression, window-deactivation cancellation and one-step undo. Direct dragging
and gizmo snapping were checked in orthographic and perspective views. It reported no QML
warnings. Existing primitive-interaction, gizmo/deletion and staged-render acceptance also
passed. Captures were inspected under `build/curve-interaction-review`.

These tests exposed inaccurate orthographic ray construction and perspective free-drag depth
in the earlier projection helper. Shared camera-based rays and view-plane translation replaced
that helper; surface hit positions and released-snap plane motion now match the displayed
camera in both projections. The editing overlay preserves type colors above the selection
outline, using shared camera parameters and native marker buffers.

The recorded gesture run measured curve projection p95 **0.084 ms** and surface snapping p95
**0.094 ms** on the small, transformed loft/two-SCP fixture. Complete capture runs include
startup, image capture and scripted waits (frame-interval p95 about 78 ms); these are not an
interactive FPS guarantee. The large staged-render regression retained old geometry and passed
resource-lifetime checks; result publication stayed below 0.5 ms in that run.

Direct ownership review: input bindings, transient gesture state, native curve queries,
authored subdivision and presentation have separate owners. Preview does not enter history;
confirmed insertion and snapping use existing shared commands and transactions. Snapping uses
leased displayed geometry, including read-only context, and creates no persistent attachment.
Native query buffers are cached by authored geometry/frame revision. No scheduler replacement
or duplicate Blender runtime was added.

The rebuilt portable application passed all checks from a separate folder with a minimal
PATH and no development Python/Qt settings. The compiled batch check now covers subdivision
and editable save/reopen as well as existing imports, attachments, deformers, deletion,
rendering and desktop startup. Qualification exposed and fixed two integration defects:
offscreen viewports now supply an inactive input context, and batch references can index
the tuple-valued curve collections returned by inspection. The latter has a regression test.
The report and packaged screenshots are under `build/curve-interaction-review/portable`.

### Axis views and continuous editing (2026-10-17)

1/2/3 now centers the active selection in X/Y/Z orthographic views and preserves apparent
zoom. G/R/S starts modal mouse transforms with confirm/cancel. View changes capture a new
gesture reference frame while retaining the original transaction and undo snapshot. Existing
direct-point and gizmo drags use the same recapture boundary. Mouse coordinates are copied
when captured; a Qt value-property alias initially made the modal start position follow the
cursor, which the actual-input acceptance exposed and the value copy corrected.

Surface snapping supports signed normal offset through the wheel, with reset on middle-click
or modifier release. Reset input is consumed before it can become orbit or transform release.
Normals are evaluated natively with nonuniform/mirrored transforms. Rotation/scale of curve
points includes their handles; previously only the selected point positions were transformed.
The correction is shared by keyboard and gizmo transforms and has regression coverage.

The development gate passed **396 tests**, including native axis rotation, transformed normals,
handle transformations/cancellation and captured reset-button release. Native contracts,
type/style and 15-line checks passed. `tools/view_gesture_acceptance.py` verified actual
keyboard/mouse/wheel behavior for zoom/centering, uninterrupted direct/gizmo/modal edits,
axis constraints, one-step undo, signed offsets, target switching and text-entry isolation.
Existing curve-interaction and usability acceptance also passed with no QML warnings.
Captures under `build/view-gesture-review` were visually inspected.

Direct ownership review: keyboard policy owns bindings; physical input capture owns wheel/
button delivery; gesture adapters own pointer mapping; the existing transform adapters own
recapture and shared commands. Native code owns axis-angle conversion and surface normals.
No new history, scheduler or persistence mechanism was introduced. Camera changes remain
workspace presentation state; snapping offset remains temporary gesture state.

The rebuilt portable application passed qualification after relocation to
`%TEMP%/anthroforge-013-views-qualified`, with a minimal PATH and development Python/Qt
settings removed. Imports, attachments, primitives, deformers, deletion, subdivision,
save/reopen, rendering and GUI startup passed. Packaged QML and both native DLLs match the
tested sources/build. The packaged desktop capture was visually inspected; qualification
results and captures are under `build/view-gesture-review/portable`. The detailed gesture
acceptance above runs against the source application, separately from portable smoke checks.

## Codex Cloud preparation (2026-10-17)

Revision `cb51bbc` passed [remote Linux and Windows qualification](https://github.com/ctrl0alt0del/native_anthroforge/actions/runs/39039142051).
Both jobs built the portable C++ library and passed CTest, all **396 pytest tests**, the
separate primitive/deformer CLI save/reopen workshop, and Python wheel/source packaging.
Ubuntu 24.04 ran the exact `tools/cloud/setup.sh`, including host library checks,
ShellCheck and clang-tidy, then successfully ran refresh in a separate shell.
Windows Server ran the same core gate. The local Windows development gate also passed
396 tests, native/PowerShell style checks, optional numerical imports and native loading.

The clean runners exposed platform-specific file-lock typing and compiler diagnostics
inside imported Happly, Eigen and the preserved addon attachment kernel. The fixes keep
warnings scoped to those include boundaries; authored native code retains warnings as
errors. The algorithms and immutable migration reference were not changed.

The actual Codex Cloud setup exposed an unprivileged base image without sudo and a
read-only home binary/cache location. Setup now uses pinned uv, Python, validation tools
and cache under the checkout. It can use existing compiler/runtime libraries, checks
that they load, and retains the complete gate. It does not silently skip missing tools.
The `cloud` dependency group pins clang-tidy and ShellCheck without changing runtime
dependencies or requiring Linux desktop release support.

Ownership review: shell scripts own environment preparation and refresh; `check_core.py`
owns the cross-platform validation sequence; storage owns platform-specific locking;
native include adapters own imported compiler accommodations. Application scheduling,
geometry algorithms and UI behavior are unchanged. Cloud/core checks do not certify
Windows GUI gestures, GPU behavior, standalone executable packaging or new anatomy.
Account environment publication and a fresh-task check are tracked separately from CI.

The actual Codex Cloud setup session also passed at `cb51bbc` on Linux/glibc 2.41:
`bash tools/cloud/setup.sh` exited zero in 136 seconds; its JUnit report recorded 396 tests,
zero failures/errors/skips (4.349 seconds). The report confirmed the owned native library,
Python 3.12.12, NumPy 1.26.4, PySide6 6.12.0 and native style checking. Refresh and native
loading passed in a new shell, with no tracked changes. This was a fresh setup after the
first trial's executor became unavailable, not a report inferred from GitHub CI.

The environment was published as **AnthroForge Standalone**, with **Only me** visibility.
A fresh task then loaded the preserved uv 0.9.29, Python 3.12.12 and native ABI 1 without
setup or dependency installation, and passed the entire gate with `UV_OFFLINE=1` and
Python downloads disabled: **396 passed, zero errors/failures/skips** (4.520 seconds).
Native contracts/style, CLI save/reopen and wheel/source checks passed; Git remained clean.

Offline refresh could not resolve the editable-build helper `editables` from cache. Normal
refresh initially hit the default shell sandbox's network restriction. Retrying through
the runtime's supported additional network-permission path passed with the Package managers
allowlist enforced. Separate-shell doctor and the CLI workshop passed afterward. This did
not change security settings, source files or Git remotes. Dependency refresh may require
package access; fully offline dependency changes are not a promised capability.

Account evidence: [setup session](https://chatgpt.com/local/01a14a2e-948d-7224-908c-a4776cc8a044)
and [fresh-task verification](https://chatgpt.com/local/01a14a36-2da3-7609-8e41-9bab9cffa04b)
are account-private records. Source/build qualification is at `cb51bbc`; later documentation
updates do not change the qualified code. The publication capture is a local ignored artifact
under `build/cloud-review`, not a required runtime file.

## Camera restoration (2026-10-17)

At `a3667ad`, the Windows development gate passed all **396 tests**, native build/CTest,
style/type checks, numerical dependency imports and native loading. The real-window
`camera_restore_acceptance.py` passed perspective and orthographic restoration after mixed
axis keys/buttons and projection/zoom changes, repeat/no-op restore, subsequent snapshots,
the View menu action, text focus, rebinding, workspace invalidation and persisted camera values.
`view_gesture_acceptance.py` passed restore during direct/gizmo/modal editing and Ctrl-snapping,
with no point jump, retained snap offset, one-step undo and cancellation. Neither run reported
QML warnings. Original/restored and active-edit captures were inspected visually under
`build/camera-restore-review` and `build/view-gesture-review`.

Ownership review: the existing viewport owns a bounded, transient camera snapshot and the
shared camera-change/rebase lifecycle. Keyboard bindings remain in the keyboard manager;
buttons and menu invoke the same viewport operation. No anatomical state, scheduler, native
geometry or project-format responsibilities changed. Workspace persistence stores the current
camera using its existing path, while the temporary return point is cleared on camera loading.

The full Windows `tools/package.ps1` rebuild passed. `tools/check_portable.py` passed with
minimal PATH: import, attachments, primitives/deformers, deletion/subdivision, save/inspect,
GPU rendering and GUI smoke checks. Packaged camera QML hashes match the qualified source;
the packaged desktop capture was inspected. Evidence is in `build/camera-restore-portable-check`.
The source archive and portable documentation were refreshed; these build outputs remain local.

## Runtime profiler 0.1.4

Validated on 2026-10-17, Windows 11 x64, Python 3.12.12 and Qt/PySide6 6.12.0.
The recording service, native Qt adapter, UI controls, runtime API and report format
are described in [profiling](profiling.md). The Activity production fix remains deferred.
[Compact qualification evidence](tasks/runtime-profiler-evidence.json) preserves
measurements and capture hashes without committing the large raw traces.

The development gate passes **413 tests** before the final document-lifetime fix, plus Ruff, mypy, native CTest, native and
PowerShell function/style checks, numerical checks and the native doctor. Coverage
includes normal lifecycle/retry, unavailable collectors, active/queued/interrupted
jobs, cancellation, native hook restoration, repeated captures, byte/time eviction,
delayed batches, bounded pending spans and clipping at recording boundaries. A fresh
headless process creates/evaluates a body and exports a report without importing Qt.

Actual Qt mouse/key acceptance passed normal and Ctrl-snapped dragging with Activity
both hidden and shown, F12 start/stop inside the gesture, confirmation, cancellation,
undo, repeated recordings and text-focus preservation. Typed text was absent from the
capture. The final five drag reports had no collector loss, and retained intervals
were inside the requested start/stop times. Screenshots were visually inspected.

From the final visible-Activity snapped report alone: Activity.qml:23 binding mean
24.15 ms, Controller.notify 30.79 ms, native pick 0.084 ms and surface-normal query
0.019 ms. There were 250 generic model replacements across observed UI models.
These inclusive timings overlap and include recording perturbation. They establish
attribution, not an unprofiled speed claim or proof of a snap-specific 2x regression.
Perfetto v58.2 imported the final trace as 114,256 slices with no nonzero error stats.

A 34-second stress capture with a two-second window received 641,880 events,
intentionally evicted 611,079, retained exactly two seconds and had zero collector
loss. Default desktop storage is partitioned conservatively: 64 MiB retained event
storage plus 64 MiB reserved for bounded queues, metadata, observers and export.
A default-budget recording separately reached the byte bound, evicting oldest events
while staying below 64 MiB of charged retained storage. Qt's transient producer
allocations are outside this owned-storage budget; it is not a process RSS ceiling.

### Overhead interpretation

Trials ran serially with system utilization recorded, without concurrent builds.
The initial normal/snapped handler means were 24.88/29.18 ms with Qt support disabled,
25.75/29.09 dormant, and 35.25/40.52 recording. Four counterbalanced trials per idle
mode after 60 warm-up moves gave 31.62/32.01 versus 31.30/32.38 ms; run standard
deviations were 0.26–0.57 ms. Warm-up adds Activity history, so absolute values from
these series must not be pooled. Later valid foreground comparisons changed the
sign of the cold idle difference. A separate nonactivating-window series is retained
as supplementary evidence; it changes presentation conditions.

The small cold/first-use differences are not a zero-overhead guarantee. No stable
steady-state idle penalty was resolved above the observed variation in the warmed
series. Recording has a substantial, measured observer effect in this binding-heavy
case; directly measured costs and comparison estimates are reported separately.
Forced disk caching was investigated and not adopted. Two supplementary foreground
trials lost window focus and canceled their gesture; they are excluded, not counted
as passing timing trials. The diagnostic now detects this interruption explicitly.

### Ownership review

Reviewed separately from tests: the recorder owns no anatomy, accepted geometry,
undo entries or scheduler policy. The desktop controller owns the Qt-independent
service across document replacement; headless sessions own or explicitly borrow it. Shared
commands, transactions, native binding registration and coordinator stages supply
coverage. Qt private APIs are isolated in one pinned native adapter. Render events
stay in C++; the generic model observer is installed only during recording. Stop
freezes application spans, clips delayed Qt data, resets periodic flush wiring and
streams bounded records to atomic export. Failure retains a frozen capture for retry;
restarts wait for the previous exporter to finish. No Activity-specific timing marker
or production Activity optimization was introduced. GPU timing, detailed stack
sampling and report viewing remain outside this release.
Final lifecycle review found and corrected New retaining stale recording controls and
headless Open losing task observation. The full GUI acceptance passes after the fixes,
including New before recording and New/Open during recording. Focus and gestures are
preserved; closing a borrowing session releases native observation without stopping
the application recorder.
