# AnthroForge development validation

Current release qualification is in [Primitive and deformer release 0.1.2](#primitive-and-deformer-release-012).
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
